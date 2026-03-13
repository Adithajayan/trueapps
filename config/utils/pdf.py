import requests
from django.template.loader import render_to_string
from django.http import HttpResponse

# നിന്റെ API Key ഇവിടെ സുരക്ഷിതമാണ്
PDFSHIFT_API_KEY = "sk_378157a06109f041f13b7f22f8aaa793ff195081"

def generate_pdf(template_name, context, filename):
    # 1. ടെംപ്ലേറ്റും ഡാറ്റയും ചേർത്ത് HTML ഉണ്ടാക്കുന്നു
    html_content = render_to_string(template_name, context)

    try:
        # 2. PDFShift API-ലേക്ക് അയക്കുന്നു
        response = requests.post(
            "https://api.pdfshift.io/v3/convert/pdf",
            auth=("api", PDFSHIFT_API_KEY),  # <--- ഇവിടെയാണ് മാറ്റം വരുത്തിയത് ("api" ചേർത്തു)
            json={
                "source": html_content,
                "use_print": True,
                "sandbox": False,
                "margin": "10mm"
            },
            timeout=30
        )

        # 3. സക്സസ് ആണെങ്കിൽ PDF തിരികെ നൽകുന്നു
        if response.status_code == 200:
            django_response = HttpResponse(response.content, content_type="application/pdf")
            django_response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return django_response
        else:
            # എറർ ഉണ്ടെങ്കിൽ അത് മെസ്സേജ് ആയി കാണിക്കും
            return HttpResponse(f"PDF Conversion Error: {response.text}", status=response.status_code)

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Connection Error: {str(e)}", status=500)