export interface SkillGroup {
  title: string;
  items: string[];
}

export interface ExperienceEntry {
  companyName: string;
  companyLocation: string;
  companyLogoSrc: string;
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
      title: "Core",
      items: ["Python", "Flask", "FastAPI", "React", "TypeScript"],
    },
    {
      title: "Architecture",
      items: ["Design Systems", "Testing"],
    },
    {
      title: "Tooling",
      items: ["Bun", "Git", "Docker", "Claude", "Codex"],
    },
  ],
  experience: [
    {
      companyName: "Apple",
      companyLocation: "Austin, TX",
      companyLogoSrc: "/images/company-logos/apple.svg",
      position: "Automation Engineer / AMP Growth Marketing",
      impact: "Engineered a full-stack application to automate end-to-end validation workflows for in-app campaign ads across all Apple Media Products (i.e. Music, TV+).",
      skills: ["Workflow Automation", "Python", "Flask", "React", "PostgreSQL", "SQLAlchemy", "Swift", "XCUITest", "iOS Devices", "Ant Design", "Kubernetes", "Docker", "AWS (S3)"],
    },
    {
      companyName: "Amazon",
      companyLocation: "Austin, TX",
      companyLogoSrc: "/images/company-logos/amazon.svg",
      position: "Software Development Engineer in Test / Amazon Glow",
      impact: "Built CI dashboards and enhanced test frameworks for firmware of Amazon Glow devices.",
      skills: ["Test Automation", "Python", "React", "PostgreSQL", "Firmware Testing", "PyTest", "Java", "Appium", "ADB"],
    },
    {
      companyName: "Hulu",
      companyLocation: "Santa Monica, CA",
      companyLogoSrc: "/images/company-logos/hulu.svg",
      position: "Software Developer in Test / Video QE",
      impact: "Embedded with Live Pipeline team to develop integration tests for an end-to-end test framework (Hulu-in-a-Box), part of a cross-functional Video QE team inititive.",
      skills: ["Test Automation", "Python", "PyTest", "Redis", "Docker", "Integration Testing", "Video Streaming", "AWS (S3)"],
    },
    {
      companyName: "Rackspace",
      companyLocation: "San Antonio, TX",
      companyLogoSrc: "/images/company-logos/rackspace.svg",
      position: "Software Developer",
      impact: "Developed and maintained features for a business-critial monolithic web application; performed ETL processes to consolidate client contacts from various datasources.",
      skills: ["Backend", "Python", "JavaScript", "Query Language", "PostgreSQL", "ETL", "Flask"],
    },
    {
      companyName: "Rackspace",
      companyLocation: "San Antonio, TX",
      companyLogoSrc: "/images/company-logos/rackspace.svg",
      position: "Software Developer in Test",
      impact: "Created automated tests for various billing components.",
      skills: ["Test Automation", "Python", "Custom Test Frameworks", "Integration Testing", "Billing Systems"],
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
      href: "https://leetcode.com/u/rgj7/",
    },
    {
      label: "CodeAbbey",
      href: "https://www.codeabbey.com/index/user_profile/whoisrgj",
    },
    {
      label: "Project Euler",
      href: "https://projecteuler.net/",
    }
  ],
  contact: {
    emailUser: "raul",
    emailDomain: "whoisrgj",
    emailTld: "com",
    linkedin: "https://www.linkedin.com/in/raulgj/",
    github: "https://github.com/rgj7",
  },
};
