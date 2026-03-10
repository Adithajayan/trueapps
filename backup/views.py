from django.conf import settings
from django.http import FileResponse
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def manual_backup(request):
    db_path = settings.DATABASES['default']['NAME']
    response = FileResponse(open(db_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename="backup.sqlite3"'
    return response