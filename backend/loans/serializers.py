from rest_framework import serializers
from rest_framework.settings import api_settings
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from core.serializers import BaseBankSerializer
from authentication.models import ApplicantStatus, LoanProvider
from banks.models import Bank
from authentication.serializers import LoanProviderSubSerializer, LoanCustomerSubSerializer
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
        data['customer'] = LoanCustomerSubSerializer(instance.customer, context=self.context).data
        data['provider'] = LoanProviderSubSerializer(instance.provider, context=self.context).data
        return data

    def calculate_monthly_payable_amount(self, validated_data):
        # Monthly Payment = Principal * Monthly Interest Rate * ((1 + Monthly Interest Rate) ^ Loan Duration in Months) 
        #                   / 
        #                   (((1 + Monthly Interest Rate) ^ Loan Duration in Months) - 1)
        monthly_interest_rate = validated_data['plan'].annual_interest_rate / Decimal(100) / Decimal(12)
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
    
    def validate_disbursibility(self, instance):
        provider_total_funds = LoanProvider.objects.filter(pk=instance.provider_id).values_list('total_funds', flat=True).first()
        if instance.amount > provider_total_funds:
            raise serializers.ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [_('Loan Provider does not have enough funds')]})

    def is_disbursed(self, validated_data):
        return 'status' in validated_data and validated_data['status'] == LoanStatus.DISBURSED.value

    def deposit_loan_amount_to_bank(self, instance):
        with transaction.atomic():
            # Deduct loan amount from provider's account
            instance.provider.total_funds = F('total_funds') - instance.amount
            instance.provider.save(update_fields=['total_funds'])
            # Add the deducted amount total funds of the bank
            instance.bank.total_funds = F('total_funds') + instance.amount
            instance.bank.save(update_fields=['total_funds'])

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if not self.is_disbursed(validated_data):
                return instance
            
            self.validate_disbursibility(instance)
            self.deposit_loan_amount_to_bank(instance)
            # TODO: Generate loan payment schedule
        
        return instance


class LoanPaymentSerializer(BaseBankSerializer):

    class Meta:
        model = LoanPayment
        exclude = BaseBankSerializer.Meta.exclude
