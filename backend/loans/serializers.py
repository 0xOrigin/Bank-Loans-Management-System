from rest_framework import serializers
from rest_framework.settings import api_settings
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from core.serializers import BaseBankSerializer
from authentication.serializers import LoanProviderSubSerializer, LoanCustomerSubSerializer
from authentication.models import ApplicantStatus, UserRole, LoanProvider
from banks.models import Bank
from loans.models import LoanStatus, LoanPlan, Loan, LoanPayment


class LoanPlanSerializer(BaseBankSerializer):

    class Meta:
        model = LoanPlan
        exclude = BaseBankSerializer.Meta.exclude + ('bank',)
    
    def create(self, validated_data):
        validated_data['bank'] = self.context['request'].user.role_object.bank
        return super().create(validated_data)


class LoanSerializer(BaseBankSerializer):

    class Meta:
        model = Loan
        exclude = BaseBankSerializer.Meta.exclude + ('bank',)
        extra_kwargs = {
            'plan': {'required': True, 'allow_null': False},
            'customer': {'required': True, 'allow_null': False},
            'provider': {'required': True, 'allow_null': False},
            'amount': {'required': True, 'allow_null': False},
            'monthly_payable_amount': {'read_only': True},
            'total_payable_amount': {'read_only': True},
            'approved_at': {'read_only': True},
            'disbursed_at': {'read_only': True},
            'is_active': {'read_only': True},
            'is_amortized': {'read_only': True},
            'status': {'read_only': True},
        }
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['plan'] = LoanPlanSerializer(instance.plan, context=self.context).data
        if self.context['request'].user.role in [UserRole.LOAN_PROVIDER.value, UserRole.BANK_PERSONNEL.value]:
            data['customer'] = LoanCustomerSubSerializer(instance.customer, context=self.context).data
        if self.context['request'].user.role in [UserRole.LOAN_CUSTOMER.value, UserRole.BANK_PERSONNEL.value]:
            data['provider'] = LoanProviderSubSerializer(instance.provider, context=self.context).data
        return data

    def calculate_monthly_interest_rate(self, annual_interest_rate):
        return Decimal(annual_interest_rate / Decimal(100) / Decimal(12))

    def calculate_monthly_payable_amount(self, validated_data):
        # Monthly Payment = Principal * Monthly Interest Rate * ((1 + Monthly Interest Rate) ^ Loan Duration in Months) 
        #                   / 
        #                   (((1 + Monthly Interest Rate) ^ Loan Duration in Months) - 1)
        monthly_interest_rate = self.calculate_monthly_interest_rate(validated_data['plan'].annual_interest_rate)
        first_part_of_equation = validated_data['amount'] * monthly_interest_rate * ((1 + monthly_interest_rate) ** validated_data['plan'].duration_in_months)
        second_part_of_equation = (((1 + monthly_interest_rate) ** validated_data['plan'].duration_in_months) - 1)
        return first_part_of_equation / second_part_of_equation

    def calculate_total_payable_amount(self, validated_data):
        return validated_data['monthly_payable_amount'] * validated_data['plan'].duration_in_months

    def validate_plan(self, value):
        if value.bank_id != self.context['request'].user.role_object.bank_id:
            raise serializers.ValidationError(_('Invalid plan'))
        return value
    
    def amount_is_within_plan_range(self, validated_data):
        if 'amount' not in validated_data or 'plan' not in validated_data:
            return
        if validated_data['amount'] < validated_data['plan'].minimum_amount or validated_data['amount'] > validated_data['plan'].maximum_amount:
            raise serializers.ValidationError(_('Amount is not within plan range'))

    def validate_customer(self, value):
        if value.bank_id != self.context['request'].user.role_object.bank_id:
            raise serializers.ValidationError(_('Invalid customer'))
        if value.status != ApplicantStatus.APPROVED.value:
            raise serializers.ValidationError(_('Customer is not approved for loan application'))
        return value

    def validate_provider(self, value):
        if value.bank_id != self.context['request'].user.role_object.bank_id:
            raise serializers.ValidationError(_('Invalid provider'))
        if value.status != ApplicantStatus.APPROVED.value:
            raise serializers.ValidationError(_('Provider is not approved for loan application'))
        return value
    
    def validate(self, attrs):
        attrs = super().validate(attrs)
        self.amount_is_within_plan_range(attrs)
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            validated_data['monthly_payable_amount'] = self.calculate_monthly_payable_amount(validated_data)
            validated_data['total_payable_amount'] = self.calculate_total_payable_amount(validated_data)
            validated_data['bank'] = self.context['request'].user.role_object.bank
            instance = super().create(validated_data)

        return instance
    
    def validate_releasability(self, instance):
        provider_total_funds = LoanProvider.objects.filter(pk=instance.provider_id).values_list('total_funds', flat=True).first()
        if instance.amount > provider_total_funds:
            raise serializers.ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [_('Loan Provider does not have enough funds')]})

    def is_released(self, validated_data):
        return 'status' in validated_data and validated_data['status'] == LoanStatus.RELEASED.value

    def is_disbursed(self, validated_data):
        return 'status' in validated_data and validated_data['status'] == LoanStatus.DISBURSED.value

    def deposit_loan_amount_to_bank(self, instance):
        with transaction.atomic():
            # Deduct loan amount from provider's account
            LoanProvider.objects.filter(pk=instance.provider_id).update(
                total_funds=F('total_funds') - instance.amount
            )
            # Add the deducted amount to the bank
            Bank.objects.filter(pk=instance.bank_id).update(
                available_funds=F('available_funds') + instance.amount,
                total_funds=F('total_funds') + instance.amount
            )

    def disburse_loan(self, instance):
        with transaction.atomic():
            Bank.objects.filter(pk=instance.bank_id).update(
                available_funds=F('available_funds') - instance.amount,
                total_loans=F('total_loans') + instance.amount
            )

    def generate_payment_schedule(self, instance):
        payment_schedules = []
        remaining_principal = instance.amount
        monthly_interest_rate = self.calculate_monthly_interest_rate(instance.plan.annual_interest_rate)
        
        for month in range(1, instance.plan.duration_in_months + 1):
            interest_paid = remaining_principal * monthly_interest_rate
            principal_paid = instance.monthly_payable_amount - interest_paid
            remaining_principal = Decimal(remaining_principal - principal_paid) if remaining_principal > principal_paid else Decimal(0)
            payment_schedule = LoanPayment(
                created_by=self.context['request'].user, created_at=timezone.now(),
                installment_number=month, loan=instance, amount=instance.monthly_payable_amount,
                due_date=(instance.approved_at + timezone.timedelta(days=30 * month)),
                interest_paid=interest_paid, principal_paid=principal_paid, remaining_principal=remaining_principal
            )
            payment_schedules.append(payment_schedule)
        
        with transaction.atomic():
            LoanPayment.objects.bulk_create(payment_schedules)

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = super().update(instance, validated_data)

            if self.is_released(validated_data):
                self.validate_releasability(instance)
                self.deposit_loan_amount_to_bank(instance)
            
            if self.is_disbursed(validated_data):
                self.disburse_loan(instance)
                self.generate_payment_schedule(instance)
        
        return instance


class AmortizationScheduleSerializer(BaseBankSerializer):
    
    class Meta:
        model = LoanPayment
        exclude = BaseBankSerializer.Meta.exclude + ('loan',)


class LoanPaymentSerializer(BaseBankSerializer):

    class Meta:
        model = LoanPayment
        exclude = BaseBankSerializer.Meta.exclude + (
            'loan', 'interest_paid', 'principal_paid', 'remaining_principal',
            'is_paid', 'paid_at',
        )

    def is_paid(self, validated_data, instance):
        if instance.is_paid:
            raise serializers.ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [_('Payment already paid')]})
        return (
            'is_paid' in validated_data and validated_data['is_paid']
            and 'paid_at' in validated_data and validated_data['paid_at']
        )

    def update_bank_funds(self, instance):
        with transaction.atomic():
            Bank.objects.filter(pk=instance.loan.bank_id).update(
                total_loans=F('total_loans') - instance.principal_paid,
                available_funds=F('available_funds') + instance.amount,
                total_funds=F('total_funds') + instance.interest_paid
            )

    def is_last_payment(self, instance):
        return (
            instance.installment_number == instance.loan.plan.duration_in_months
        )

    def update(self, instance, validated_data):
        with transaction.atomic():
            if not self.is_paid(validated_data, instance):
                raise serializers.ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [_('No updates to perform')]})
            instance = super().update(instance, validated_data)
            self.update_bank_funds(instance)
            if self.is_last_payment(instance):
                instance.loan.is_active = False
                instance.loan.is_amortized = True
                instance.loan.save(update_fields=['is_active', 'is_amortized'])
        
        return instance
