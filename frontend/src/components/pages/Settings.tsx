import React from 'react';
import { useTheme } from '../theme-provider';

const SettingCard: React.FC<{
  title: string;
  description: string;
  children: React.ReactNode;
}> = ({ title, description, children }) => (
  <div className="card-enhanced">
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div className="flex-1">
        <h3 className="text-lg font-medium text-foreground">{title}</h3>
        <p className="text-sm text-muted-foreground mt-1">{description}</p>
      </div>
      <div className="flex-shrink-0">
        {children}
      </div>
    </div>
  </div>
);

const ThemeSettings: React.FC = () => {
  const { theme, setTheme } = useTheme();
  
  return (
    <div className="flex gap-3">
      {['light', 'dark', 'system'].map((themeOption) => (
        <button
          key={themeOption}
          onClick={() => setTheme(themeOption as any)}
          className={`px-4 py-2 rounded-lg transition-all duration-200 capitalize ${
            theme === themeOption
              ? 'bg-primary text-primary-foreground'
              : 'bg-card border border-border hover:bg-accent'
          }`}
        >
          {themeOption}
        </button>
      ))}
    </div>
  );
};

export const Settings: React.FC = () => {
  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Settings</h1>
        <p className="text-muted-foreground mt-1">
          Configure your ProxyWhirl experience
        </p>
      </div>

      <div className="space-y-6">
        <SettingCard
          title="Theme Preference"
          description="Choose your preferred color scheme"
        >
          <ThemeSettings />
        </SettingCard>

        <SettingCard
          title="Auto Validation"
          description="Automatically validate proxies on startup"
        >
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              defaultChecked
              className="w-4 h-4 rounded border-border text-primary focus:ring-primary focus:ring-offset-0"
            />
            <span className="text-sm">Enable auto validation</span>
          </label>
        </SettingCard>

        <SettingCard
          title="Notification Preferences"
          description="Configure when to receive notifications"
        >
          <div className="space-y-2">
            {[
              'Proxy validation failures',
              'System health alerts',
              'Weekly reports'
            ].map((option) => (
              <label key={option} className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  defaultChecked={option !== 'Weekly reports'}
                  className="w-4 h-4 rounded border-border text-primary focus:ring-primary focus:ring-offset-0"
                />
                <span className="text-sm">{option}</span>
              </label>
            ))}
          </div>
        </SettingCard>

        <SettingCard
          title="Data Retention"
          description="How long to keep proxy validation history"
        >
          <select className="px-3 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-ring">
            <option value="7">7 days</option>
            <option value="30" selected>30 days</option>
            <option value="90">90 days</option>
            <option value="365">1 year</option>
          </select>
        </SettingCard>

        <SettingCard
          title="Export Data"
          description="Download your proxy configuration and history"
        >
          <div className="flex gap-2">
            <button className="px-4 py-2 bg-card border border-border rounded-lg hover:bg-accent transition-colors">
              Export Config
            </button>
            <button className="px-4 py-2 bg-card border border-border rounded-lg hover:bg-accent transition-colors">
              Export History
            </button>
          </div>
        </SettingCard>

        <div className="card-enhanced border-destructive/20">
          <h3 className="text-lg font-medium text-destructive mb-2">Danger Zone</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Actions in this section cannot be undone
          </p>
          <div className="flex flex-col sm:flex-row gap-3">
            <button className="px-4 py-2 bg-destructive/10 text-destructive border border-destructive/20 rounded-lg hover:bg-destructive/20 transition-colors">
              Clear All History
            </button>
            <button className="px-4 py-2 bg-destructive/10 text-destructive border border-destructive/20 rounded-lg hover:bg-destructive/20 transition-colors">
              Reset Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
