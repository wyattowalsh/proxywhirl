import { createElement } from 'react';
import { loader } from 'fumadocs-core/source';
import { createMDXSource } from 'fumadocs-mdx';
import { docs } from '@/.source';
import { icons as lucideIcons, type LucideIcon } from 'lucide-react';
import * as Ai from 'react-icons/ai';
import * as Bi from 'react-icons/bi';
import * as Bs from 'react-icons/bs';
import * as Cg from 'react-icons/cg';
import * as Ci from 'react-icons/ci';
import * as Di from 'react-icons/di';
import * as Fa from 'react-icons/fa';
import * as Fa6 from 'react-icons/fa6';
import * as Fc from 'react-icons/fc';
import * as Fi from 'react-icons/fi';
import * as Gi from 'react-icons/gi';
import * as Go from 'react-icons/go';
import * as Gr from 'react-icons/gr';
import * as Hi from 'react-icons/hi';
import * as Hi2 from 'react-icons/hi2';
import * as Im from 'react-icons/im';
import * as Io from 'react-icons/io';
import * as Io5 from 'react-icons/io5';
import * as Lia from 'react-icons/lia';
import * as Lu from 'react-icons/lu';
import * as Md from 'react-icons/md';
import * as Pi from 'react-icons/pi';
import * as Ri from 'react-icons/ri';
import * as Si from 'react-icons/si';
import * as Sl from 'react-icons/sl';
import * as Tb from 'react-icons/tb';
import * as Tfi from 'react-icons/tfi';
import * as Ti from 'react-icons/ti';
import * as Vsc from 'react-icons/vsc';
import * as Wi from 'react-icons/wi';

const iconSets = {
  ai: Ai,
  bi: Bi,
  bs: Bs,
  cg: Cg,
  ci: Ci,
  di: Di,
  fa: Fa,
  fa6: Fa6,
  fc: Fc,
  fi: Fi,
  gi: Gi,
  go: Go,
  gr: Gr,
  hi: Hi,
  hi2: Hi2,
  im: Im,
  io: Io,
  io5: Io5,
  lia: Lia,
  lu: Lu,
  md: Md,
  pi: Pi,
  ri: Ri,
  si: Si,
  sl: Sl,
  tb: Tb,
  tfi: Tfi,
  ti: Ti,
  vsc: Vsc,
  wi: Wi,
};

const ReactIcon = ({ icon: iconString }: { icon: string }): React.ReactElement | null => {
  const [prefix, iconName] = iconString.split('/');

  if (!prefix || !iconName) {
    return null;
  }

  const iconSet = iconSets[prefix as keyof typeof iconSets];

  if (!iconSet) {
    return null;
  }

  const IconComponent = iconSet[iconName as keyof typeof iconSet] as React.ComponentType;

  if (IconComponent) {
    return createElement(IconComponent);
  }

  return null;
};

// See https://fumadocs.vercel.app/docs/headless/source-api for more info
export const source = loader({
  // it assigns a URL to your pages
  baseUrl: '/docs',
  source: docs.toFumadocsSource(),
  icon(icon) {
    if (!icon) return;

    // Support for lucide icons
    if (icon in lucideIcons) {
      return createElement(lucideIcons[icon as keyof typeof lucideIcons]);
    }

    // Support for all react-icons
    if (icon.includes('/')) {
      return createElement(ReactIcon, { icon });
    }

    return;
  },
});
