// Test CVA imports
console.log('Testing CVA imports...');

import { cva } from 'class-variance-authority';
console.log('cva:', cva);

// Try different import approaches
try {
  const { VariantProps } = require('class-variance-authority');
  console.log('VariantProps (require):', VariantProps);
} catch (e) {
  console.log('VariantProps require failed:', e.message);
}

export default function CVATest() {
  const button = cva('btn', {
    variants: {
      intent: {
        primary: 'btn-primary',
        secondary: 'btn-secondary'
      }
    }
  });

  return (
    <div>
      <h2>CVA Test Component</h2>
      <button className={button({ intent: 'primary' })}>Test Button</button>
    </div>
  );
}