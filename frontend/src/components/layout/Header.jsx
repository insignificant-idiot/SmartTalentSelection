import { Link, useLocation } from "react-router-dom";
import { Briefcase, Upload, TrendingUp } from "lucide-react";

export default function Header() {
  const location = useLocation();
  const navItems = [
    { path: "/", label: "Dashboard", icon: Briefcase },
    { path: "/upload", label: "Upload", icon: Upload },
    { path: "/ranking", label: "Ranking", icon: TrendingUp },
  ];
  return (
    <header className="bg-gray-900 border-b border-gray-800 sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Briefcase className="h-8 w-8 text-blue-500" />
            <span className="ml-2 text-xl font-bold text-white">
              TalentEngine
            </span>
          </div>
          <nav className="flex space-x-4">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${location.pathname === item.path ? "bg-gray-800 text-white" : "text-gray-300 hover:bg-gray-700 hover:text-white"}`}
              >
                <item.icon className="h-4 w-4 mr-2" />
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
}
