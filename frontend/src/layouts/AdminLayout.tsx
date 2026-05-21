import { useEffect, useState, type ReactNode } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import {
  FileTextIcon,
  LayoutDashboardIcon,
  LogOutIcon,
  SettingsIcon,
} from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { getMe } from "@/lib/api";

interface AdminLayoutProps {
  children?: ReactNode;
}

const navItems = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboardIcon },
  { title: "Posts", url: "/dashboard/posts", icon: FileTextIcon },
  { title: "Settings", url: "/dashboard/settings", icon: SettingsIcon },
];

export function AdminLayout({ children }: AdminLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }

    getMe(token)
      .then((user) => setUsername(user.username))
      .catch(handleLogout);
  }, [navigate]);

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    navigate("/login");
  }

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full">
        <Sidebar collapsible="icon">
          <SidebarHeader className="px-4 py-3">
            <h2 className="text-sm font-semibold">Admin</h2>
          </SidebarHeader>
          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupContent>
                <SidebarMenu>
                  {navItems.map((item) => {
                    const isActive = location.pathname === item.url;
                    return (
                      <SidebarMenuItem key={item.url}>
                        <SidebarMenuButton
                          asChild
                          isActive={isActive}
                          tooltip={item.title}
                        >
                          <a href={item.url}>
                            <item.icon />
                            <span>{item.title}</span>
                          </a>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    );
                  })}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
          <SidebarFooter className="p-4">
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton
                  onClick={handleLogout}
                  tooltip="Logout"
                >
                  <LogOutIcon />
                  <span>Logout</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarFooter>
          <SidebarRail />
        </Sidebar>
        <main className="flex flex-1 flex-col overflow-hidden">
          <header className="flex h-12 items-center gap-2 border-b px-4">
            <SidebarTrigger />
          </header>
          <div className="flex-1 overflow-auto p-6">
            {children ?? <Outlet />}
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
}

export default AdminLayout;
