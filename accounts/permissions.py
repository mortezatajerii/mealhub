# accounts/permissions.py
from rest_framework.permissions import BasePermission
from .models import User

WILDCARD = "*"
Role = User.Role


class Perm:
    # menus
    MENU_VIEW = "menu.view"
    MENU_MANAGE = "menu.manage"
    FOOD_ITEM_MANAGE = "food_item.manage"

    # organizations
    ORG_VIEW = "organization.view"
    ORG_CREATE = "organization.create"
    ORG_MANAGE = "organization.manage"
    ORG_ASSIGN_ADMIN = "organization.assign_admin"

    # departments & employees
    DEPARTMENT_VIEW = "department.view"
    DEPARTMENT_MANAGE = "department.manage"
    DEPARTMENT_ASSIGN_ADMIN = "department.assign_admin"
    EMPLOYEE_VIEW = "employee.view"
    EMPLOYEE_CREATE = "employee.create"

    # reservations
    RESERVATION_CREATE = "reservation.create"
    RESERVATION_VIEW = "reservation.view"
    RESERVATION_MANAGE = "reservation.manage"

    # reports
    REPORT_ORDERS = "report.orders"
    REPORT_FINANCIAL = "report.financial"

    # finance
    INVOICE_VIEW = "invoice.view"
    INVOICE_ISSUE = "invoice.issue"
    WALLET_CREDIT = "wallet.credit"

    # employee
    EMPLOYEE_VIEW = "employee.view"
    EMPLOYEE_CREATE = "employee.create"
    EMPLOYEE_MANAGE = "employee.manage"


class Scope:
    PLATFORM = "platform"
    ORGANIZATION = "organization"
    DEPARTMENT = "department"
    SELF = "self"


ROLE_PERMISSIONS = {
    Role.SUPER_ADMIN: {WILDCARD},
    Role.PLATFORM_MANAGER: {
        Perm.MENU_VIEW,
        Perm.MENU_MANAGE,
        Perm.FOOD_ITEM_MANAGE,
        Perm.ORG_VIEW,
        Perm.ORG_CREATE,
        Perm.ORG_MANAGE,
        Perm.ORG_ASSIGN_ADMIN,
        Perm.DEPARTMENT_VIEW,
        Perm.DEPARTMENT_MANAGE,
        Perm.EMPLOYEE_VIEW,
        Perm.EMPLOYEE_CREATE,
        Perm.EMPLOYEE_MANAGE,
        Perm.RESERVATION_VIEW,
        Perm.RESERVATION_MANAGE,
        Perm.REPORT_ORDERS,
        Perm.REPORT_FINANCIAL,
        Perm.INVOICE_VIEW,
        Perm.INVOICE_ISSUE,
        Perm.WALLET_CREDIT,
    },
    Role.MENU_MANAGER: {
        Perm.MENU_VIEW,
        Perm.MENU_MANAGE,
        Perm.FOOD_ITEM_MANAGE,
    },
    Role.ACCOUNT_MANAGER: {
        Perm.ORG_VIEW,
        Perm.ORG_CREATE,
        Perm.ORG_MANAGE,
        Perm.ORG_ASSIGN_ADMIN,
        Perm.DEPARTMENT_VIEW,
        Perm.EMPLOYEE_VIEW,
    },
    Role.RESTAURANT_MANAGER: {
        Perm.ORG_VIEW,
        Perm.MENU_VIEW,
        Perm.REPORT_ORDERS,
    },
    Role.FINANCE: {
        Perm.ORG_VIEW,
        Perm.REPORT_ORDERS,
        Perm.REPORT_FINANCIAL,
        Perm.INVOICE_VIEW,
        Perm.INVOICE_ISSUE,
        Perm.WALLET_CREDIT,
    },
    Role.COMPANY_OWNER: {
        Perm.ORG_VIEW,
        Perm.DEPARTMENT_VIEW,
        Perm.DEPARTMENT_ASSIGN_ADMIN,
        Perm.EMPLOYEE_VIEW,
        Perm.EMPLOYEE_CREATE,
        Perm.EMPLOYEE_MANAGE,
        Perm.RESERVATION_VIEW,
        Perm.REPORT_ORDERS,
        Perm.REPORT_FINANCIAL,
        Perm.INVOICE_VIEW,
        Perm.MENU_VIEW,
    },
    Role.DEPARTMENT_ADMIN: {
        Perm.DEPARTMENT_VIEW,
        Perm.EMPLOYEE_VIEW,
        Perm.EMPLOYEE_CREATE,
        Perm.EMPLOYEE_MANAGE,
        Perm.RESERVATION_VIEW,
        Perm.REPORT_ORDERS,
        Perm.MENU_VIEW,
    },
    Role.EMPLOYEE: {
        Perm.MENU_VIEW,
        Perm.RESERVATION_CREATE,
        Perm.RESERVATION_VIEW,
    },
}


ROLE_SCOPES = {
    Role.SUPER_ADMIN: Scope.PLATFORM,
    Role.PLATFORM_MANAGER: Scope.PLATFORM,
    Role.MENU_MANAGER: Scope.PLATFORM,
    Role.ACCOUNT_MANAGER: Scope.PLATFORM,
    Role.RESTAURANT_MANAGER: Scope.PLATFORM,
    Role.FINANCE: Scope.PLATFORM,
    Role.COMPANY_OWNER: Scope.ORGANIZATION,
    Role.DEPARTMENT_ADMIN: Scope.DEPARTMENT,
    Role.EMPLOYEE: Scope.SELF,
}


def get_role_permissions(role):
    return ROLE_PERMISSIONS.get(role, set())


def get_user_scope(user):
    if getattr(user, "is_superuser", False):
        return Scope.PLATFORM
    return ROLE_SCOPES.get(getattr(user, "role", None), Scope.SELF)


def user_has_perm(user, permission):
    if not (user and user.is_authenticated):
        return False
    if user.is_superuser:
        return True
    granted = get_role_permissions(getattr(user, "role", None))
    return WILDCARD in granted or permission in granted


class HasPermission(BasePermission):
    """
    permission لازم را از خود ویو می‌خواند:

        permission_map = {"list": Perm.MENU_VIEW, "create": Perm.MENU_MANAGE}
        required_permission = Perm.MENU_VIEW   # حالت تک‌دسترسی

    اگر برای یک action هیچ permission اعلام نشده باشد، درخواست رد می‌شود.
    """

    def get_required_permission(self, request, view):
        permission_map = getattr(view, "permission_map", None) or {}
        action = getattr(view, "action", None)
        if action in permission_map:
            return permission_map[action]
        if "default" in permission_map:
            return permission_map["default"]
        return getattr(view, "required_permission", None)

    def has_permission(self, request, view):
        permission = self.get_required_permission(request, view)
        if permission is None:
            return False
        return user_has_perm(request.user, permission)
