from pathlib import Path

import qrcode
from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

from .models import Livraison


def livraison_qr_png(request, livraison_id):
    """Return (and persist) a PNG QR for the livraison delivery code.

    Behaviour:
    - If MEDIA_ROOT/livraison_qr/<id>.png exists, serve it (FileResponse).
    - Otherwise generate it, save to MEDIA, then serve it.

    This keeps a copy in media for inspection and avoids regenerating repeatedly.
    """
    livraison = get_object_or_404(Livraison, id=livraison_id)
    code = livraison.delivery_code or ""
    if not code:
        raise Http404("No delivery code for this livraison")

    media_root = Path(getattr(settings, "MEDIA_ROOT", ""))
    if not media_root:
        # In case MEDIA_ROOT not configured, fallback to tmp and still serve
        media_root = Path("/tmp")

    qr_dir = media_root / "livraison_qr"
    qr_dir.mkdir(parents=True, exist_ok=True)

    file_path = qr_dir / f"{livraison_id}.png"
    if not file_path.exists():
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(str(code))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        # Save as PNG
        img.save(str(file_path))

    # Serve the file
    return FileResponse(open(file_path, "rb"), content_type="image/png")
