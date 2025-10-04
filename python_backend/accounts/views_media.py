import uuid, mimetypes, os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from commons.obs import obs_client
from django.contrib.auth import get_user_model

User = get_user_model()

BUCKET = os.getenv("OBS_BUCKET")

class PresignAvatarView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        content_type = request.data.get("content_type", "image/jpeg")
        if not content_type.startswith("image/"):
            return Response({"detail":"invalid content_type"}, status=400)

        ext = mimetypes.guess_extension(content_type) or ""
        key = f"avatars/{request.user.id}/{uuid.uuid4().hex}{ext}"

        url = obs_client().generate_presigned_url(
            "put_object",
            Params={
                "Bucket": BUCKET, "Key": key, 
                "ContentType": content_type,
            },
            ExpiresIn=600,  # 10 minutos
        )
        return Response({"upload_url": url, "key": key})

class AvatarUrlView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.avatar_key:
            return Response({"url": None})

        url = obs_client().generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET, 
                "Key": request.user.avatar_key,
                "ResponseContentType": "image/jpeg",
            },
            ExpiresIn=3600
        )
        return Response({"url": url})

class ConfirmAvatarView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        key = request.data.get("key")
        if not key or not key.startswith(f"avatars/{request.user.id}/"):
            return Response({"detail": "invalid key"}, status=400)

        c = obs_client()
        try:
            head = c.head_object(Bucket=BUCKET, Key=key)
            if head.get("ContentLength", 0) > 5 * 1024 * 1024:
                return Response({"detail": "image too large"}, status=400)
            if not str(head.get("ContentType", "")).startswith("image/"):
                return Response({"detail": "invalid mime"}, status=400)
        except Exception:
            return Response({"detail": "object not found"}, status=400)

        old = request.user.avatar_key
        request.user.avatar_key = key
        request.user.save(update_fields=["avatar_key"])

        if old and old != key:
            try:
                c.delete_object(Bucket=BUCKET, Key=old)
            except Exception:
                pass

        return Response({"avatar_key": key})
