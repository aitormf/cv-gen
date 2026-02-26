"""Data models for CV content."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ContactInfo:
    name: str = ""
    title: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""
    photo: str = ""


@dataclass
class Section:
    heading: str
    slug: str
    content_html: str
    section_type: str = "other"  # profile, experience, education, skills, languages, projects, certifications, other


SIDEBAR_TYPES = {"skills", "languages", "certifications"}
MAIN_TYPES = {"profile", "experience", "education", "projects", "other"}


@dataclass
class CVData:
    contact: ContactInfo = field(default_factory=ContactInfo)
    sections: list[Section] = field(default_factory=list)

    def sidebar_sections(self) -> list[Section]:
        return [s for s in self.sections if s.section_type in SIDEBAR_TYPES]

    def main_sections(self) -> list[Section]:
        return [s for s in self.sections if s.section_type in MAIN_TYPES]
