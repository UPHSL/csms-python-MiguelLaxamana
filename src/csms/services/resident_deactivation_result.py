from dataclasses import dataclass

from csms.models.resident import Resident


@dataclass
class ResidentDeactivationResult:
    success: bool
    resident: Resident | None = None
    not_found: bool = False
    already_inactive: bool = False

    @classmethod
    def successful(
        cls,
        resident: Resident,
    ) -> "ResidentDeactivationResult":
        return cls(
            success=True,
            resident=resident,
            not_found=False,
            already_inactive=False,
        )

    @classmethod
    def already_inactive_result(
        cls,
        resident: Resident,
    ) -> "ResidentDeactivationResult":
        return cls(
            success=True,
            resident=resident,
            not_found=False,
            already_inactive=True,
        )

    @classmethod
    def resident_not_found(
        cls,
    ) -> "ResidentDeactivationResult":
        return cls(
            success=False,
            resident=None,
            not_found=True,
            already_inactive=False,
        )