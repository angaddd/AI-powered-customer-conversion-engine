def get_user_company(user):
    membership = user.company_memberships.select_related("company").first()
    return membership.company if membership else None


class TenantScopedMixin:
    company_field = "company"

    def get_company(self):
        return get_user_company(self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        company = self.get_company()
        if not company:
            return queryset.none()
        return queryset.filter(**{self.company_field: company})

    def perform_create(self, serializer):
        serializer.save(company=self.get_company())

