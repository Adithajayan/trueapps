import requests
from django.template.loader import render_to_string
from django.http import HttpResponse


PDFSHIFT_API_KEY = "sk_378157a06109f041f13b7f22f8aaa793ff195081"

def generate_pdf(template_name, context, filename):

    html_content = render_to_string(template_name, context)


    response = requests.post(
        "https://api.pdfshift.io/v3/convert/pdf",
        auth=(PDFSHIFT_API_KEY, ""),
        json={
            "source": html_content,
            "use_print": True,
            "sandbox": False,
            "margin": "10mm"
        }
    )


    if response.status_code == 200:
        django_response = HttpResponse(response.content, content_type="application/pdf")
        django_response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return django_response
    else:

        return HttpResponse(f"Error: {response.text}", status=response.status_code)