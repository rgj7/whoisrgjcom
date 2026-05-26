export interface SkillGroup {
  title: string;
  items: string[];
}

export interface ExperienceEntry {
  company: string;
  position: string;
  impact: string;
  skills: string[];
}

export interface ProfileLink {
  label: string;
  href: string;
}

export interface EducationEntry {
  school: string;
  degree: string;
  period: string;
  details?: string;
}

export interface DevProfile {
  name: string;
  tagline: string;
  intro: string;
  imageSrc: string;
  imageAlt: string;
  skills: SkillGroup[];
  experience: ExperienceEntry[];
  education: EducationEntry[];
  codingProfiles: ProfileLink[];
  contact: {
    emailUser: string;
    emailDomain: string;
    emailTld: string;
    linkedin: string;
    github: string;
  };
}

export const devProfile: DevProfile = {
  name: "Raul Gonzalez",
  tagline: "Software Engineer",
  intro:
    "8+ years of experience in backend, automation and testing. Hands-on experience building impactful web apps and tools at Apple, Amazon, and Hulu.",
  imageSrc: "/images/dev-profile.jpg",
  imageAlt: "Portrait photo",
  skills: [
    {
      title: "Frontend",
      items: ["React", "JavaScript", "TypeScript", "Tailwind CSS", "shadcn/ui"],
    },
    {
      title: "Backend",
      items: ["Python", "FastAPI", "Flask", "SQLAlchemy", "PostgreSQL"],
    },
    {
      title: "Tooling",
      items: ["Bun", "Git", "Docker", "Claude", "Codex"],
    },
  ],
  experience: [
    {
      company: "Apple / Austin, TX",
      position: "Automation Engineer / Growth Marketing",
      impact: "Engineered a full-stack application to automate end-to-end validation workflows for in-app campaign ads across all Apple Media Products (i.e. Music, TV+).",
      skills: ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL"],
    },
    {
      company: "Amazon / Austin, TX",
      position: "Software Development Engineer in Test / Amazon Glow",
      impact: "Built CI dashboards and enhanced test frameworks for firmware of Amazon Glow devices.",
      skills: ["Python", "CI/CD", "Test Automation", "Firmware", "Dashboards"],
    },
    {
      company: "Hulu / Santa Monica, CA",
      position: "Software Developer in Test / Video QE",
      impact: "Embedded with Live Pipeline team to develop integration tests for an end-to-end test framework (Hulu-in-a-Box), part of a cross-functional Video QE team inititive.",
      skills: ["Python", "Integration Testing", "Video Streaming", "Automation"],
    },
    {
      company: "Rackspace / San Antonio, TX",
      position: "Software Developer",
      impact: "Developed and maintained features for a business-critial monolithic Python backend; performed ETL processes to consolidate client contacts from various datasources.",
      skills: ["Python", "ETL", "SQL", "Monolith"],
    },
    {
      company: "Rackspace / San Antonio, TX",
      position: "Software Developer in Test",
      impact: "Created automated tests for various billing components.",
      skills: ["Test Automation", "Python", "Billing Systems"],
    },
  ],
  education: [
    {
      school: "The University of Texas at San Antonio",
      degree: "B.S. in Computer Science",
      period: "Graduated 2015",
      details: "Dual concentration in Software Engineering / Computer and Information Security.",
    },
  ],
  codingProfiles: [
    {
      label: "LeetCode",
      href: "https://leetcode.com/",
    },
    {
      label: "Codeforces",
      href: "https://codeforces.com/",
    },
  ],
  contact: {
    emailUser: "raul",
    emailDomain: "whoisrgj",
    emailTld: "com",
    linkedin: "https://www.linkedin.com/in/raulgj/",
    github: "https://github.com/rgj7",
  },
};
