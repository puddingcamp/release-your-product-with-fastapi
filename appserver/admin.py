from sqladmin import Admin

from appserver.apps.account.admin import OAuthAccountAdmin, UserAdmin
from appserver.apps.calendar.admin import BookingAdmin, BookingFileAdmin, CalendarAdmin, TimeSlotAdmin


def include_admin_views(admin: Admin):
    admin.add_view(UserAdmin)
    admin.add_view(CalendarAdmin)
    admin.add_view(TimeSlotAdmin)
    admin.add_view(BookingAdmin)
    admin.add_view(BookingFileAdmin)
    admin.add_view(OAuthAccountAdmin)
    