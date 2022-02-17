

from django.http import HttpRequest
from django.http import JsonResponse

def upload_file_view(request: HttpRequest):
    if request.method == "POST":
        
        if (file:=request.FILES.get("file")):
            with open("media/test1.png", 'wb') as f:
                lines = file.readlines()
                for line in lines:
                    f.write(line)
            # file.write("test.png")
            # file.close()
            #check if video or photo
            #preprocessing
            #prediction
            return JsonResponse({"message":"good", "prediction":"banana"}) # return the prediction to the client
        return JsonResponse({"message":"bad", "description":"no files attached"})
    return JsonResponse({"message": "bad", "description":"method not allowed"}, status=405)
