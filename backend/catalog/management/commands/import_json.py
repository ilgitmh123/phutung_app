import json
from pathlib import Path
from django.core.management.base import BaseCommand
from catalog.models import Product
from catalog.utils_import import normalize_item


class Command(BaseCommand):
    help = "Import JSON vào Product (upsert theo oem_code)"

    def add_arguments(self, parser):
        parser.add_argument("json_path", type=str, help="Đường dẫn tới file JSON")
        parser.add_argument(
            "--mode",
            choices=["insert", "update", "upsert"],
            default="upsert",
            help="insert = chỉ thêm mới, update = chỉ cập nhật, upsert = cả 2",
        )
        parser.add_argument("--dry-run", action="store_true", help="Chạy thử, không ghi DB")
        parser.add_argument("--default-brand", type=str, default="Honda")

    def handle(self, json_path, mode, dry_run, default_brand, *args, **kwargs):
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        report = {"ok": 0, "fail": 0, "items": []}

        for sku, raw in data.items():
            try:
                normalized = normalize_item(sku, raw, default_brand=default_brand)

                if dry_run:
                    self.stdout.write(f"[DRY-RUN] {sku} → {normalized['name']}")
                    report["ok"] += 1
                    report["items"].append({"sku": sku, "dry_run": True})
                    continue

                if mode == "insert":
                    obj, created = Product.objects.get_or_create(
                        oem_code=sku,
                        defaults=normalized,
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"[INSERTED] {sku}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"[SKIPPED] {sku} đã tồn tại"))
                        continue

                elif mode == "update":
                    obj = Product.objects.get(oem_code=sku)
                    for k, v in normalized.items():
                        setattr(obj, k, v)
                    obj.save()
                    created = False
                    self.stdout.write(self.style.SUCCESS(f"[UPDATED] {sku}"))

                else:  # upsert
                    obj, created = Product.objects.update_or_create(
                        oem_code=sku,
                        defaults=normalized,
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"[CREATED] {sku}"))
                    else:
                        self.stdout.write(self.style.SUCCESS(f"[UPDATED] {sku}"))

                report["ok"] += 1
                report["items"].append({"sku": sku, "created": created})

            except Exception as e:
                report["fail"] += 1
                report["items"].append({"sku": sku, "error": str(e), "raw": raw})
                self.stdout.write(self.style.ERROR(f"[ERROR] {sku}: {e}"))

        out = Path(json_path).with_suffix(".report.json")
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(
            f"Import xong: OK={report['ok']} FAIL={report['fail']} → {out}"
        ))
