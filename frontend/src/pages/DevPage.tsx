import { useRef, useState } from "react";
import type React from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import GithubIcon from "@/components/ui/icons/github-icon";
import LinkedinIcon from "@/components/ui/icons/linkedin-icon";
import MailFilledIcon from "@/components/ui/icons/mail-filled-icon";
import type { AnimatedIconHandle } from "@/components/ui/types";
import { devProfile } from "@/lib/dev-profile";
import { DefaultLayout } from "@/layouts/DefaultLayout";

function getCompanyAcronym(companyName: string) {
  return companyName
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0]?.toUpperCase() ?? "")
    .join("") || "--";
}

function ExperienceLogo({ companyName, logoSrc }: { companyName: string; logoSrc: string }) {
  const [hasError, setHasError] = useState(false);

  return (
    <div
      className="mx-auto flex size-20 shrink-0 items-center justify-center rounded-sm border border-border/70 bg-zinc-50 dark:bg-zinc-100"
      aria-hidden="true"
    >
      {hasError ? (
        <span className="text-sm font-semibold text-muted-foreground">{getCompanyAcronym(companyName)}</span>
      ) : (
        <img
          src={logoSrc}
          alt=""
          aria-hidden="true"
          className="size-14 object-contain"
          onError={() => setHasError(true)}
        />
      )}
    </div>
  );
}

export function DevPage() {
  const mailIconRef = useRef<AnimatedIconHandle>(null);
  const linkedinIconRef = useRef<AnimatedIconHandle>(null);
  const githubIconRef = useRef<AnimatedIconHandle>(null);

  const handleEmailClick = (event: React.MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault();
    const { emailUser, emailDomain, emailTld } = devProfile.contact;
    window.location.href = `mailto:${emailUser}@${emailDomain}.${emailTld}`;
  };

  return (
    <DefaultLayout>
      <section className="grid gap-6 md:grid-cols-[1.2fr_1fr] md:items-center">
      <div className="space-y-3">
        <p className="text-sm text-muted-foreground">/dev</p>
        <h1 className="text-3xl font-bold tracking-tight md:text-4xl">{devProfile.name}</h1>
        <p className="text-base font-medium text-muted-foreground">{devProfile.tagline}</p>
        <p className="text-muted-foreground">{devProfile.intro}</p>
        <div className="flex flex-wrap gap-2 pt-1">
          <Button asChild>
            <a
              href="#"
              className="gap-2"
              onClick={handleEmailClick}
              onMouseEnter={() => mailIconRef.current?.startAnimation()}
              onMouseLeave={() => mailIconRef.current?.stopAnimation()}
            >
              <MailFilledIcon ref={mailIconRef} className="size-5" />
              Email
            </a>
          </Button>
          <Button variant="secondary" className="btn-linkedin" asChild>
            <a
              href={devProfile.contact.linkedin}
              target="_blank"
              rel="noreferrer"
              className="gap-2"
              onMouseEnter={() => linkedinIconRef.current?.startAnimation()}
              onMouseLeave={() => linkedinIconRef.current?.stopAnimation()}
            >
              <LinkedinIcon ref={linkedinIconRef} className="size-5" />
              LinkedIn
            </a>
          </Button>
          <Button variant="secondary" className="btn-github" asChild>
            <a
              href={devProfile.contact.github}
              target="_blank"
              rel="noreferrer"
              className="gap-2"
              onMouseEnter={() => githubIconRef.current?.startAnimation()}
              onMouseLeave={() => githubIconRef.current?.stopAnimation()}
            >
              <GithubIcon ref={githubIconRef} className="size-5" />
              GitHub
            </a>
          </Button>
        </div>
      </div>
      <div className="overflow-hidden rounded-2xl border bg-muted/20">
        <img src={devProfile.imageSrc} alt={devProfile.imageAlt} className="h-full w-full object-cover" />
      </div>
    </section>

    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">My Journey Thus Far...</h2>
      <div className="relative space-y-3 md:space-y-4">
        <div
          className="pointer-events-none absolute top-0 bottom-0 left-3 hidden w-px border-l border-dashed border-muted-foreground/40 md:block"
          aria-hidden="true"
        />

        {devProfile.experience.map((item) => (
          <div key={`${item.companyName}-${item.position}`} className="relative md:pl-10">
            <span
              className="absolute top-1/2 left-[7px] hidden size-3 -translate-y-1/2 rounded-full border border-muted-foreground/50 bg-background md:block"
              aria-hidden="true"
            />
            <div className="grid gap-1 rounded-lg border border-transparent p-1 sm:grid-cols-[7rem_1fr] sm:items-center sm:gap-3">
              <ExperienceLogo companyName={item.companyName} logoSrc={item.companyLogoSrc} />
              <div>
                <p className="font-semibold leading-tight">{item.position}</p>
                <p className="text-sm text-muted-foreground">{item.companyName} / {item.companyLocation}</p>
                <p className="mt-1 text-sm text-muted-foreground">{item.impact}</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {item.skills.map((skill) => (
                    <Badge key={`${item.companyName}-${item.position}-${skill}`} variant="secondary">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>

    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">Education</h2>
      <div className="space-y-7">
        {devProfile.education.map((item) => (
          <div key={`${item.school}-${item.degree}`} className="grid gap-3 rounded-lg border border-transparent p-1 sm:grid-cols-[8.5rem_1fr] sm:gap-8">
            <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">{item.period}</p>
            <div>
              <p className="font-semibold leading-tight">{item.degree}</p>
              <p className="text-sm text-muted-foreground">{item.school}</p>
              {item.details ? <p className="mt-1 text-sm text-muted-foreground">{item.details}</p> : null}
            </div>
          </div>
        ))}
      </div>
    </section>

      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Coding profiles</h2>
        <div className="flex flex-wrap gap-2">
          {devProfile.codingProfiles.map((profile) => (
            <Button key={profile.href} variant="outline" asChild>
              <a href={profile.href} target="_blank" rel="noreferrer">
                {profile.label}
              </a>
            </Button>
          ))}
        </div>
        <div className="flex flex-wrap">
          <a href="https://www.codeabbey.com/index/user_profile/whoisrgj" target="_blank">
            <img src="https://www.codeabbey.com/index/user_banner/whoisrgj.png" />
          </a>
        </div>
      </section>
    </DefaultLayout>
  );
}

export default DevPage;
