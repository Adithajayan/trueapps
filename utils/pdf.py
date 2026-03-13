import requests
from django.template.loader import render_to_string
from django.http import HttpResponse

PDFSHIFT_API_KEY = "sk_378157a06109f041f13b7f22f8aaa793ff195081"


def generate_pdf(template, context, filename):

    html = render_to_string(template, context)

    response = requests.post(
        "https://api.pdfshift.io/v3/convert/pdf",
        auth=("api", PDFSHIFT_API_KEY),
        json={
            "source": html
        }
    )

    pdf = response.content

    django_response = HttpResponse(pdf, content_type="application/pdf")
    django_response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return django_response