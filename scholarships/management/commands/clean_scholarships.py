import re
import sys

from django.core.management.base import BaseCommand

from scholarships.models import Scholarship


class Command(BaseCommand):
    help = (
        "Clean scholarship fields by stripping extra/non-standard "
        "text into the notes field"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview changes without saving",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        total = Scholarship.objects.count()
        changed = 0

        for s in Scholarship.objects.iterator():
            notes_parts = []
            changed_fields = []

            # -- contents (award amount) --
            cleaned, extra = self._clean_contents(s.contents)
            if extra:
                notes_parts.append(f"[Contents] {extra}")
                s.contents = cleaned
                changed_fields.append("contents")

            # -- plural_grants --
            cleaned, extra = self._clean_plural_grants(s.plural_grants)
            if extra:
                notes_parts.append(f"[Plural Grants] {extra}")
                s.plural_grants = cleaned
                changed_fields.append("plural_grants")

            # -- duration --
            cleaned, extra = self._clean_duration(s.duration)
            if extra:
                notes_parts.append(f"[Duration] {extra}")
                s.duration = cleaned
                changed_fields.append("duration")

            # -- grantees --
            cleaned, extra = self._clean_grantees(s.grantees)
            if extra:
                notes_parts.append(f"[Grantees] {extra}")
                s.grantees = cleaned
                changed_fields.append("grantees")

            # -- grantees_applications --
            cleaned, extra = self._clean_grantees_applications(s.grantees_applications)
            if extra:
                notes_parts.append(f"[Grantees/Applications] {extra}")
                s.grantees_applications = cleaned
                changed_fields.append("grantees_applications")

            # -- qualifier --
            cleaned, extra = self._clean_qualifier(s.qualifier)
            if extra:
                notes_parts.append(f"[Qualifier] {extra}")
                s.qualifier = cleaned
                changed_fields.append("qualifier")

            # -- application_period --
            cleaned, extra = self._clean_generic_garbage(s.application_period)
            if extra:
                notes_parts.append(f"[Application Period] {extra}")
                s.application_period = cleaned
                changed_fields.append("application_period")

            # -- address_contact --
            cleaned, extra = self._clean_generic_garbage(s.address_contact)
            if extra:
                notes_parts.append(f"[Address/Contact] {extra}")
                s.address_contact = cleaned
                changed_fields.append("address_contact")

            # -- additional_requirements --
            cleaned, extra = self._clean_generic_garbage(s.additional_requirements)
            if extra:
                notes_parts.append(f"[Additional Requirements] {extra}")
                s.additional_requirements = cleaned
                changed_fields.append("additional_requirements")

            # -- designated_schools --
            cleaned, extra = self._clean_generic_garbage(s.designated_schools)
            if extra:
                notes_parts.append(f"[Designated Schools] {extra}")
                s.designated_schools = cleaned
                changed_fields.append("designated_schools")

            # -- designated_fields --
            cleaned, extra = self._clean_generic_garbage(s.designated_fields)
            if extra:
                notes_parts.append(f"[Designated Fields] {extra}")
                s.designated_fields = cleaned
                changed_fields.append("designated_fields")

            # -- selection_method --
            cleaned, extra = self._clean_generic_garbage(s.selection_method)
            if extra:
                notes_parts.append(f"[Selection Method] {extra}")
                s.selection_method = cleaned
                changed_fields.append("selection_method")

            if not notes_parts:
                continue

            changed += 1
            all_notes = "\n".join(notes_parts)
            if s.notes:
                s.notes = s.notes.rstrip("\n") + "\n" + all_notes
            else:
                s.notes = all_notes

            safe_name = s.scholarship_name.encode(
                sys.stdout.encoding or "utf-8", errors="replace"
            ).decode(sys.stdout.encoding or "utf-8")
            safe_notes = all_notes.encode(
                sys.stdout.encoding or "utf-8", errors="replace"
            ).decode(sys.stdout.encoding or "utf-8")

            if dry_run:
                self.stdout.write(
                    f"[DRY-RUN] {safe_name} — {', '.join(changed_fields)}"
                )
                self.stdout.write(f"  Notes to add: {safe_notes}")
                self.stdout.write("---")
            else:
                s.save(update_fields=changed_fields + ["notes"])

        self.stdout.write(
            self.style.SUCCESS(
                f"{'[DRY-RUN] ' if dry_run else ''}"
                f"Processed {total} scholarships, cleaned {changed}."
            )
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    GARBAGE_PATTERN = re.compile(r"[^\x20-\x7E\n\r\t]")

    @staticmethod
    def _strip_garbage(text):
        return Command.GARBAGE_PATTERN.sub("", text).strip()

    @staticmethod
    def _clean_generic_garbage(text):
        """Strip non-ASCII garbage characters from a field."""
        if not text:
            return "", ""
        cleaned = Command._strip_garbage(text)
        removed = Command._find_removed(text, cleaned)
        return cleaned, removed

    @staticmethod
    def _find_removed(original, cleaned):
        """Return a string describing what was removed, or empty."""
        if original == cleaned:
            return ""
        removed_chars = set(original) - set(cleaned)
        parts = []
        for ch in sorted(removed_chars, key=ord):
            if ch in "\n\r\t ":
                continue
            codepoint = f"U+{ord(ch):04X}"
            name = f"\\x{ord(ch):02x}" if ord(ch) < 256 else codepoint
            parts.append(f"garbled char {name}")
        return "; ".join(parts) if parts else "non-printable characters removed"

    @staticmethod
    def _clean_contents(text):
        """Keep only award-amount lines (e.g. 200/Y, 20/M, Up to 40/M, Max 4000/y)."""
        if not text:
            return "", ""
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        if not lines:
            return "", ""
        amount_patterns = [
            re.compile(r"^[\d,.\-–—]+\s*/\s*[YM]$"),  # 200/Y, 300-500/Y
            re.compile(r"^[\d,.\-–—]+\s*/\s*[YM],?$"),  # 120/M,
            re.compile(r"^[\d,.\-–—]+$"),  # 50000, 1,500
            re.compile(r"^Up to [\d,./YM]+$", re.IGNORECASE),  # Up to 40/M
            re.compile(r"^Max [\d,./ym]+$", re.IGNORECASE),  # Max 4000/y
            re.compile(r"^About [\d]+$", re.IGNORECASE),  # About 20
            re.compile(r"^Within the budget$", re.IGNORECASE),
        ]
        is_amount = [any(p.match(ln) for p in amount_patterns) for ln in lines]
        if all(is_amount):
            return text, ""
        if not any(is_amount):
            cleaned = Command._strip_garbage(text)
            return cleaned, ""
        keep = [ln for ln, a in zip(lines, is_amount) if a]
        extra = [ln for ln, a in zip(lines, is_amount) if not a]
        result = "\n".join(keep)
        extra_str = "; ".join(extra)
        return result, extra_str

    @staticmethod
    def _clean_plural_grants(text):
        """Keep only first line (Y/N)."""
        if not text:
            return "", ""
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        if not lines:
            return "", ""
        first = lines[0].upper()
        if first in ("Y", "N"):
            keep = first
            extra = "; ".join(lines[1:]) if len(lines) > 1 else ""
        else:
            keep = lines[0]
            extra = "; ".join(lines[1:]) if len(lines) > 1 else ""
        return keep, extra

    @staticmethod
    def _is_duration_core(line):
        """Check if a line is a core duration piece (not payment schedule details)."""
        extra_keywords = [
            "payment",
            "scholarship payment",
            "scholarship",
            "july",
            "dec",
            "apr",
            "mar",
        ]
        lower = line.lower()
        if any(kw in lower for kw in extra_keywords):
            return False
        if re.match(r"^[a-z]+\.?\)$", lower):
            return False
        return True

    @staticmethod
    def _clean_duration(text):
        """Keep core duration lines; move payment schedule details to notes."""
        if not text:
            return "", ""
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        if not lines:
            return "", ""
        is_core = [Command._is_duration_core(ln) for ln in lines]
        if all(is_core):
            cleaned = Command._strip_garbage(text)
            return cleaned, ""
        if not any(is_core):
            cleaned = Command._strip_garbage(text)
            return cleaned, ""
        keep = [ln for ln, c in zip(lines, is_core) if c]
        extra = [ln for ln, c in zip(lines, is_core) if not c]
        result = "\n".join(keep)
        extra_str = "; ".join(extra)
        return result, extra_str

    @staticmethod
    def _is_grantee_clean(line):
        """Check if line is a clean grantee count."""
        patterns = [
            re.compile(r"^\d+$"),
            re.compile(r"^\d{1,3}(?:,\d{3})+$"),
            re.compile(r"^About \d+$", re.IGNORECASE),
            re.compile(r"^Up to \d+$", re.IGNORECASE),
            re.compile(r"^Maximum? of \d+$", re.IGNORECASE),
            re.compile(r"^\w+ the budget$", re.IGNORECASE),
            re.compile(r"^A few$", re.IGNORECASE),
            re.compile(r"^(Not fixed|Not fixed yet)$", re.IGNORECASE),
        ]
        return any(p.match(line) for p in patterns)

    @staticmethod
    def _clean_grantees(text):
        """Keep only the numeric grantee count."""
        if not text:
            return "", ""
        lines = [Command._strip_garbage(ln) for ln in text.split("\n") if ln.strip()]
        if not lines:
            return "", ""
        is_clean = [Command._is_grantee_clean(ln) for ln in lines]
        if all(is_clean):
            return text, ""
        if not any(is_clean):
            return text, ""
        keep = [ln for ln, c in zip(lines, is_clean) if c]
        extra = [ln for ln, c in zip(lines, is_clean) if not c]
        return "\n".join(keep), "; ".join(extra)

    @staticmethod
    def _is_ratio_clean(line):
        return bool(re.match(r"^\d+/\d+$", line))

    @staticmethod
    def _clean_grantees_applications(text):
        """Keep only numeric ratio like 15/35, 9/13."""
        if not text:
            return "", ""
        lines = [Command._strip_garbage(ln) for ln in text.split("\n") if ln.strip()]
        if not lines:
            return "", ""
        is_clean = [Command._is_ratio_clean(ln) for ln in lines]
        if all(is_clean):
            return text, ""
        if not any(is_clean):
            return text, ""
        keep = [ln for ln, c in zip(lines, is_clean) if c]
        extra = [ln for ln, c in zip(lines, is_clean) if not c]
        return "\n".join(keep), "; ".join(extra)

    @staticmethod
    def _clean_qualifier(text):
        """Strip parenthetical suffixes like (3-), (4-5), (2) from codes."""
        if not text:
            return "", ""
        lines = [Command._strip_garbage(ln) for ln in text.split("\n") if ln.strip()]
        if not lines:
            return "", ""
        cleaned_lines = []
        extra_parts = []
        any_had_parens = False
        for line in lines:
            clean = re.sub(r"\s*\([^)]*\)", "", line).strip()
            parenthetical = re.findall(r"\([^)]*\)", line)
            if parenthetical:
                any_had_parens = True
                extra_parts.append(f"{clean}: {', '.join(parenthetical)}")
            if clean:
                cleaned_lines.append(clean)
        result = "\n".join(cleaned_lines)
        if not any_had_parens:
            return text, ""
        extra = "; ".join(extra_parts)
        return result, extra
