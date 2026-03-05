from .models import User, CompanyAccount, Membership

def get_primary_membership(user: User) -> Membership:
	return Membership.objects.select_related("company").filter(user=user).first()

def can_create_role(creator_role: str, target_role: str) -> bool:
	if creator_role == Membership.Role.ADMIN:
		return target_role in {Membership.Role.MANAGER, Membership.Role.STAFF, Membership.Role.CLIENT}
	
	if creator_role == Membership.Role.MANAGER:
		return target_role in {Membership.Role.STAFF, Membership.Role.CLIENT}

	if creator_role == Membership.Role.STAFF:
		return target_role == Membership.Role.CLIENT
	
	return False