import type { ReactNode } from 'react';
import { HomeLayout } from 'fumadocs-ui/layouts/home';
import { baseOptions } from '@/app/layout.config';
import {
  HiOutlineBookOpen,
  HiOutlineClipboardDocumentList,
  HiOutlineWrenchScrewdriver,
  HiOutlineMap,
} from 'react-icons/hi2';
import { Button } from "@/components/ui/button";
import Link from 'fumadocs-core/link';

export default function Layout({ children }: { children: ReactNode }) {
  return (
  <HomeLayout 
    {...baseOptions}
    links={[
		{
			type: 'custom',
			children: <Button variant="link">
					<Link href="/docs" className="flex items-center gap-2">
						<HiOutlineBookOpen />
						Docs
					</Link>
					</Button>
		},
		{
			type: 'custom',
			children: <Button variant="link">
					<Link href="/reference" className="flex items-center gap-2">
						<HiOutlineClipboardDocumentList />
						Reference
					</Link>
					</Button>
		},
		{
			type: 'custom',
			children: <Button variant="link">
					<Link href="/contributing" className="flex items-center gap-2">
						<HiOutlineWrenchScrewdriver />
						Contributing
					</Link>
					</Button>
		},
		{
			type: 'custom',
			children: <Button variant="link">
					<Link href="/roadmap" className="flex items-center gap-2">
						<HiOutlineMap />
						Roadmap
					</Link>
					</Button>
		},

  ]}>
	{children}
  </HomeLayout>
  );
}
