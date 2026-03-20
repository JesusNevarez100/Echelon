from django.test import TestCase
from django.urls import reverse

from accounts.models import CompanyAccount, Membership, User


class AccountViewsTests(TestCase):
    def setUp(self):
        self.company = CompanyAccount.objects.create(name="Acme")
        self.other_company = CompanyAccount.objects.create(name="OtherCo")

        self.admin_user = User.objects.create_user(
            username="adminuser",
            password="StrongPass123!",
            email="admin@example.com",
            first_name="Ada",
            last_name="Admin",
        )
        self.staff_user = User.objects.create_user(
            username="staffuser",
            password="StrongPass123!",
            email="staff@example.com",
            first_name="Sam",
            last_name="Staff",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="StrongPass123!",
            email="other@example.com",
        )

        Membership.objects.create(
            user=self.admin_user,
            company=self.company,
            role=Membership.Role.ADMIN,
        )
        Membership.objects.create(
            user=self.staff_user,
            company=self.company,
            role=Membership.Role.STAFF,
        )
        Membership.objects.create(
            user=self.other_user,
            company=self.other_company,
            role=Membership.Role.ADMIN,
        )

    def test_account_detail_displays_current_user(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("accounts_custom:account_detail"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "staffuser")
        self.assertContains(response, "Acme")

    def test_edit_account_detail_updates_profile(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("accounts_custom:edit_account_detail"),
            {
                "username": "staffupdated",
                "email": "updated@example.com",
                "first_name": "Taylor",
                "last_name": "Staff",
            },
        )

        self.assertRedirects(response, reverse("accounts_custom:account_detail"))
        self.staff_user.refresh_from_db()
        self.assertEqual(self.staff_user.username, "staffupdated")
        self.assertEqual(self.staff_user.email, "updated@example.com")
        self.assertEqual(self.staff_user.first_name, "Taylor")

    def test_admin_account_list_is_limited_to_company_members(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("accounts_custom:account_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "adminuser")
        self.assertContains(response, "staffuser")
        self.assertNotContains(response, "otheruser")

    def test_non_admin_cannot_access_account_list(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("accounts_custom:account_list"))

        self.assertEqual(response.status_code, 403)
