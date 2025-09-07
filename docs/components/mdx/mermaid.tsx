"use client";

import { useEffect, useId, useRef, useState, useCallback } from "react";
import { useTheme } from "next-themes";

// Icons as React components for better performance
const ZoomInIcon = () => (
	<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
		<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
	</svg>
);

const ZoomOutIcon = () => (
	<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
		<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
	</svg>
);

const FitToScreenIcon = () => (
	<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
		<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
	</svg>
);

const ResetIcon = () => (
	<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
		<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
	</svg>
);

const NewTabIcon = () => (
	<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
		<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
	</svg>
);

const CopyIcon = () => (
	<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
		<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
	</svg>
);

const DownloadIcon = () => (
	<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
		<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
	</svg>
);

export function Mermaid({ chart }: { chart: string }) {
	const id = useId();
	const [svg, setSvg] = useState("");
	const containerRef = useRef<HTMLDivElement>(null);
	const contentRef = useRef<HTMLDivElement>(null);
	const currentChartRef = useRef<string>(null);
	const { resolvedTheme } = useTheme();
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [showTooltip, setShowTooltip] = useState<string | null>(null);
	
	// Zoom and pan state
	const [scale, setScale] = useState(1);
	const [position, setPosition] = useState({ x: 0, y: 0 });
	const [isDragging, setIsDragging] = useState(false);
	const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
	const [dragStartPosition, setDragStartPosition] = useState({ x: 0, y: 0 });
	const [contentDimensions, setContentDimensions] = useState({ width: 0, height: 0 });

	const MIN_SCALE = 0.1;
	const MAX_SCALE = 5;
	const ZOOM_STEP = 0.2;
	const CONTAINER_PADDING = 40;

	// Calculate optimal zoom to fit
	const calculateZoomToFit = useCallback(() => {
		if (!containerRef.current || !contentDimensions.width || !contentDimensions.height) {
			return 1;
		}

		const container = containerRef.current;
		const containerWidth = container.clientWidth - CONTAINER_PADDING;
		const containerHeight = container.clientHeight - CONTAINER_PADDING;

		const scaleX = containerWidth / contentDimensions.width;
		const scaleY = containerHeight / contentDimensions.height;

		// Use the smaller scale to ensure the entire diagram fits
		const optimalScale = Math.min(scaleX, scaleY, 1); // Don't zoom in beyond 100% initially
		return Math.max(optimalScale, MIN_SCALE);
	}, [contentDimensions.width, contentDimensions.height]);

	// Extract dimensions from SVG
	const extractSVGDimensions = (svgString: string) => {
		const parser = new DOMParser();
		const svgDoc = parser.parseFromString(svgString, "image/svg+xml");
		const svgElement = svgDoc.querySelector("svg");
		
		if (svgElement) {
			const viewBox = svgElement.getAttribute("viewBox");
			const width = svgElement.getAttribute("width");
			const height = svgElement.getAttribute("height");

			if (viewBox) {
				const [, , vbWidth, vbHeight] = viewBox.split(" ").map(Number);
				return { width: vbWidth, height: vbHeight };
			} else if (width && height) {
				return { 
					width: parseFloat(width.replace(/px|em|rem/, "")), 
					height: parseFloat(height.replace(/px|em|rem/, "")) 
				};
			}
		}
		
		return { width: 800, height: 600 }; // fallback dimensions
	};

	useEffect(() => {
		if (currentChartRef.current === chart || !containerRef.current) return;
		const container = containerRef.current;
		currentChartRef.current = chart;

		async function renderChart() {
			setIsLoading(true);
			setError(null);
			
			try {
				const { default: mermaid } = await import("mermaid");

				// configure mermaid
				mermaid.initialize({
					startOnLoad: false,
					securityLevel: "loose",
					fontFamily: "inherit",
					themeCSS: "margin: 0;",
					theme: resolvedTheme === "dark" ? "dark" : "default",
				});

				const { svg, bindFunctions } = await mermaid.render(
					id,
					chart.replaceAll("\\n", "\n")
				);

				bindFunctions?.(container);
				setSvg(svg);
				
				// Extract dimensions from the rendered SVG
				const dimensions = extractSVGDimensions(svg);
				setContentDimensions(dimensions);
				
				// Reset position
				setPosition({ x: 0, y: 0 });
				
				// Auto-fit on initial render
				setTimeout(() => {
					const optimalScale = calculateZoomToFit();
					setScale(optimalScale);
				}, 100);
			} catch (err) {
				console.error("Error while rendering mermaid", err);
				setError(err instanceof Error ? err.message : "Failed to render diagram");
			} finally {
				setIsLoading(false);
			}
		}

		void renderChart();
	}, [chart, id, resolvedTheme, calculateZoomToFit]);

	// Keyboard shortcuts
	useEffect(() => {
		const handleKeyDown = (e: KeyboardEvent) => {
			if (!containerRef.current?.contains(document.activeElement)) return;
			
			switch (e.key) {
				case '+':
				case '=':
					e.preventDefault();
					zoomIn();
					break;
				case '-':
					e.preventDefault();
					zoomOut();
					break;
				case '0':
					e.preventDefault();
					resetZoom();
					break;
				case 'f':
					e.preventDefault();
					zoomToFit();
					break;
				case 'n':
					if (e.ctrlKey || e.metaKey) {
						e.preventDefault();
						openInNewTab();
					}
					break;
				case 'c':
					if (e.ctrlKey || e.metaKey) {
						e.preventDefault();
						copySVG();
					}
					break;
			}
		};

		window.addEventListener('keydown', handleKeyDown);
		return () => window.removeEventListener('keydown', handleKeyDown);
	}, []);

	// Handle mouse wheel zoom with better UX
	const handleWheel = (e: React.WheelEvent) => {
		e.preventDefault();
		const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
		const newScale = Math.min(Math.max(scale + delta, MIN_SCALE), MAX_SCALE);
		setScale(newScale);
	};

	// Handle mouse down for dragging
	const handleMouseDown = (e: React.MouseEvent) => {
		if (e.button === 0) { // Left click only
			setIsDragging(true);
			setDragStart({ x: e.clientX, y: e.clientY });
			setDragStartPosition(position);
		}
	};

	// Handle mouse move for dragging
	const handleMouseMove = (e: React.MouseEvent) => {
		if (isDragging) {
			const deltaX = e.clientX - dragStart.x;
			const deltaY = e.clientY - dragStart.y;
			setPosition({
				x: dragStartPosition.x + deltaX,
				y: dragStartPosition.y + deltaY,
			});
		}
	};

	// Handle mouse up
	const handleMouseUp = () => {
		setIsDragging(false);
	};

	// Zoom controls with better UX
	const zoomIn = () => {
		const newScale = Math.min(scale + ZOOM_STEP, MAX_SCALE);
		setScale(newScale);
	};

	const zoomOut = () => {
		const newScale = Math.max(scale - ZOOM_STEP, MIN_SCALE);
		setScale(newScale);
	};

	const resetZoom = () => {
		setScale(1);
		setPosition({ x: 0, y: 0 });
	};

	const zoomToFit = () => {
		const optimalScale = calculateZoomToFit();
		setScale(optimalScale);
		setPosition({ x: 0, y: 0 });
	};

	// Copy SVG to clipboard
	const copySVG = async () => {
		try {
			await navigator.clipboard.writeText(svg);
			setShowTooltip('copied');
			setTimeout(() => setShowTooltip(null), 2000);
		} catch (err) {
			console.error('Failed to copy SVG:', err);
			setShowTooltip('copy-error');
			setTimeout(() => setShowTooltip(null), 2000);
		}
	};

	// Download SVG file
	const downloadSVG = () => {
		const blob = new Blob([svg], { type: 'image/svg+xml' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = 'mermaid-diagram.svg';
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		URL.revokeObjectURL(url);
		setShowTooltip('downloaded');
		setTimeout(() => setShowTooltip(null), 2000);
	};

	// Enhanced open in new tab with full interactivity
	const openInNewTab = () => {
		const newWindow = window.open('', '_blank');
		if (newWindow) {
			const interactiveMermaidHTML = `
<!DOCTYPE html>
<html>
<head>
	<title>Mermaid Diagram - Interactive View</title>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<style>
		* {
			margin: 0;
			padding: 0;
			box-sizing: border-box;
		}
		
		body {
			font-family: system-ui, -apple-system, sans-serif;
			background: ${resolvedTheme === 'dark' ? '#0a0a0a' : '#ffffff'};
			color: ${resolvedTheme === 'dark' ? '#ffffff' : '#000000'};
			height: 100vh;
			overflow: hidden;
			position: relative;
		}
		
		.toolbar {
			position: fixed;
			top: 16px;
			right: 16px;
			z-index: 1000;
			display: flex;
			flex-direction: column;
			gap: 8px;
			background: ${resolvedTheme === 'dark' ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.8)'};
			backdrop-filter: blur(10px);
			border-radius: 8px;
			padding: 8px;
			border: 1px solid ${resolvedTheme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'};
			box-shadow: 0 4px 20px ${resolvedTheme === 'dark' ? 'rgba(0, 0, 0, 0.3)' : 'rgba(0, 0, 0, 0.1)'};
		}
		
		.toolbar button {
			width: 40px;
			height: 40px;
			border: none;
			border-radius: 6px;
			background: ${resolvedTheme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'};
			color: ${resolvedTheme === 'dark' ? '#ffffff' : '#000000'};
			cursor: pointer;
			display: flex;
			align-items: center;
			justify-content: center;
			font-size: 18px;
			transition: all 0.2s ease;
			border: 1px solid ${resolvedTheme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'};
		}
		
		.toolbar button:hover:not(:disabled) {
			background: ${resolvedTheme === 'dark' ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.1)'};
			transform: translateY(-1px);
			box-shadow: 0 2px 8px ${resolvedTheme === 'dark' ? 'rgba(0, 0, 0, 0.3)' : 'rgba(0, 0, 0, 0.15)'};
		}
		
		.toolbar button:disabled {
			opacity: 0.5;
			cursor: not-allowed;
		}
		
		.toolbar button:active {
			transform: translateY(0);
		}
		
		.separator {
			width: 100%;
			height: 1px;
			background: ${resolvedTheme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'};
			margin: 4px 0;
		}
		
		.status {
			position: fixed;
			bottom: 16px;
			left: 16px;
			z-index: 1000;
			display: flex;
			gap: 16px;
			font-family: 'Courier New', monospace;
			font-size: 12px;
		}
		
		.status-item {
			background: ${resolvedTheme === 'dark' ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.8)'};
			backdrop-filter: blur(10px);
			padding: 8px 12px;
			border-radius: 6px;
			border: 1px solid ${resolvedTheme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'};
			color: ${resolvedTheme === 'dark' ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)'};
		}
		
		.help {
			position: fixed;
			bottom: 16px;
			right: 16px;
			z-index: 1000;
			background: ${resolvedTheme === 'dark' ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.8)'};
			backdrop-filter: blur(10px);
			padding: 8px 12px;
			border-radius: 6px;
			border: 1px solid ${resolvedTheme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'};
			font-size: 11px;
			color: ${resolvedTheme === 'dark' ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)'};
		}
		
		.container {
			width: 100vw;
			height: 100vh;
			overflow: hidden;
			cursor: grab;
			position: relative;
		}
		
		.container:active {
			cursor: grabbing;
		}
		
		.content {
			width: 100%;
			height: 100%;
			display: flex;
			align-items: center;
			justify-content: center;
			transition: transform 0.1s ease;
			transform-origin: center center;
		}
		
		.loading {
			position: fixed;
			top: 50%;
			left: 50%;
			transform: translate(-50%, -50%);
			font-size: 18px;
			color: ${resolvedTheme === 'dark' ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)'};
		}
	</style>
</head>
<body>
	<div class="loading" id="loading">Loading diagram...</div>
	<div class="container" id="container">
		<div class="content" id="content">
			${svg}
		</div>
	</div>
	
	<div class="toolbar">
		<button id="zoomIn" title="Zoom In (+)">+</button>
		<button id="zoomOut" title="Zoom Out (-)">−</button>
		<button id="zoomFit" title="Fit to Screen (F)">⊞</button>
		<button id="zoomReset" title="Reset Zoom (0)">⌂</button>
		<div class="separator"></div>
		<button id="download" title="Download SVG">⬇</button>
		<button id="copy" title="Copy SVG">📋</button>
	</div>
	
	<div class="status">
		<div class="status-item">Zoom: <span id="zoomLevel">100%</span></div>
		<div class="status-item">Size: <span id="dimensions">${Math.round(contentDimensions.width)}×${Math.round(contentDimensions.height)}</span></div>
	</div>
	
	<div class="help">
		Mouse: drag to pan, wheel to zoom • Keys: +/- zoom, 0 reset, F fit, Ctrl+C copy
	</div>
	
	<script>
		let scale = 1;
		let position = { x: 0, y: 0 };
		let isDragging = false;
		let dragStart = { x: 0, y: 0 };
		let dragStartPosition = { x: 0, y: 0 };
		
		const MIN_SCALE = 0.1;
		const MAX_SCALE = 10;
		const ZOOM_STEP = 0.2;
		
		const container = document.getElementById('container');
		const content = document.getElementById('content');
		const zoomLevel = document.getElementById('zoomLevel');
		const loading = document.getElementById('loading');
		
		// Hide loading
		setTimeout(() => loading.style.display = 'none', 100);
		
		function updateTransform() {
			content.style.transform = \`translate(\${position.x}px, \${position.y}px) scale(\${scale})\`;
			zoomLevel.textContent = Math.round(scale * 100) + '%';
		}
		
		function zoomToFit() {
			const containerRect = container.getBoundingClientRect();
			const contentRect = content.getBoundingClientRect();
			const scaleX = (containerRect.width - 80) / ${contentDimensions.width};
			const scaleY = (containerRect.height - 80) / ${contentDimensions.height};
			scale = Math.min(scaleX, scaleY, 1);
			position = { x: 0, y: 0 };
			updateTransform();
		}
		
		// Initial fit
		setTimeout(zoomToFit, 200);
		
		// Zoom controls
		document.getElementById('zoomIn').onclick = () => {
			scale = Math.min(scale + ZOOM_STEP, MAX_SCALE);
			updateTransform();
		};
		
		document.getElementById('zoomOut').onclick = () => {
			scale = Math.max(scale - ZOOM_STEP, MIN_SCALE);
			updateTransform();
		};
		
		document.getElementById('zoomFit').onclick = zoomToFit;
		
		document.getElementById('zoomReset').onclick = () => {
			scale = 1;
			position = { x: 0, y: 0 };
			updateTransform();
		};
		
		// Download functionality
		document.getElementById('download').onclick = () => {
			const blob = new Blob([\`${svg.replace(/`/g, '\\`')}\`], { type: 'image/svg+xml' });
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = 'mermaid-diagram.svg';
			a.click();
			URL.revokeObjectURL(url);
		};
		
		// Copy functionality
		document.getElementById('copy').onclick = async () => {
			try {
				await navigator.clipboard.writeText(\`${svg.replace(/`/g, '\\`')}\`);
				document.getElementById('copy').textContent = '✓';
				setTimeout(() => document.getElementById('copy').textContent = '📋', 2000);
			} catch (err) {
				console.error('Failed to copy:', err);
			}
		};
		
		// Mouse events
		container.onmousedown = (e) => {
			if (e.button === 0) {
				isDragging = true;
				dragStart = { x: e.clientX, y: e.clientY };
				dragStartPosition = { ...position };
			}
		};
		
		container.onmousemove = (e) => {
			if (isDragging) {
				position.x = dragStartPosition.x + (e.clientX - dragStart.x);
				position.y = dragStartPosition.y + (e.clientY - dragStart.y);
				updateTransform();
			}
		};
		
		container.onmouseup = () => isDragging = false;
		container.onmouseleave = () => isDragging = false;
		
		// Wheel zoom
		container.onwheel = (e) => {
			e.preventDefault();
			const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
			scale = Math.min(Math.max(scale + delta, MIN_SCALE), MAX_SCALE);
			updateTransform();
		};
		
		// Keyboard shortcuts
		document.onkeydown = (e) => {
			switch (e.key) {
				case '+':
				case '=':
					e.preventDefault();
					scale = Math.min(scale + ZOOM_STEP, MAX_SCALE);
					updateTransform();
					break;
				case '-':
					e.preventDefault();
					scale = Math.max(scale - ZOOM_STEP, MIN_SCALE);
					updateTransform();
					break;
				case '0':
					e.preventDefault();
					scale = 1;
					position = { x: 0, y: 0 };
					updateTransform();
					break;
				case 'f':
				case 'F':
					e.preventDefault();
					zoomToFit();
					break;
				case 'c':
					if (e.ctrlKey || e.metaKey) {
						e.preventDefault();
						document.getElementById('copy').click();
					}
					break;
			}
		};
		
		// Disable context menu
		container.oncontextmenu = (e) => e.preventDefault();
	</script>
</body>
</html>`;
			newWindow.document.write(interactiveMermaidHTML);
			newWindow.document.close();
		}
		setShowTooltip('opened');
		setTimeout(() => setShowTooltip(null), 2000);
	};

	// Transform style with smooth transitions
	const transformStyle = {
		transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
		transformOrigin: "center center",
		transition: isDragging ? "none" : "transform 0.15s cubic-bezier(0.4, 0, 0.2, 1)",
	};

	// Button component for consistent styling
	const ControlButton = ({ 
		onClick, 
		disabled, 
		title, 
		children, 
		variant = 'default',
		shortcut 
	}: { 
		onClick: () => void; 
		disabled?: boolean; 
		title: string; 
		children: React.ReactNode;
		variant?: 'default' | 'primary' | 'secondary';
		shortcut?: string;
	}) => (
		<button
			onClick={onClick}
			disabled={disabled}
			className={`group relative w-10 h-10 flex items-center justify-center rounded-lg border transition-all duration-200 
				${variant === 'primary' 
					? 'bg-blue-500 hover:bg-blue-600 text-white border-blue-600' 
					: variant === 'secondary'
					? 'bg-green-500 hover:bg-green-600 text-white border-green-600'
					: 'bg-background hover:bg-muted border-border hover:border-border/60'
				} 
				${disabled 
					? 'opacity-40 cursor-not-allowed' 
					: 'hover:shadow-md hover:scale-105 active:scale-95'
				}
				shadow-sm backdrop-blur-sm`}
			title={`${title}${shortcut ? ` (${shortcut})` : ''}`}
			onMouseEnter={() => setShowTooltip(title)}
			onMouseLeave={() => setShowTooltip(null)}
		>
			{children}
			{showTooltip === title && (
				<div className="absolute right-12 top-1/2 -translate-y-1/2 bg-black/90 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-50 pointer-events-none">
					{title}
					{shortcut && <span className="text-gray-400 ml-1">({shortcut})</span>}
				</div>
			)}
		</button>
	);

	if (error) {
		return (
			<div className="relative border rounded-xl overflow-hidden bg-background min-h-[400px] flex items-center justify-center">
				<div className="text-center space-y-4">
					<div className="text-red-500 text-6xl">⚠️</div>
					<div className="text-lg font-semibold text-red-600">Failed to render diagram</div>
					<div className="text-sm text-muted-foreground max-w-md">{error}</div>
					<button 
						onClick={() => window.location.reload()} 
						className="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-colors"
					>
						Reload page
					</button>
				</div>
			</div>
		);
	}

	return (
		<div className="relative border rounded-xl overflow-hidden bg-gradient-to-br from-background to-muted/30 shadow-lg">
			{/* Enhanced Control Panel */}
			<div className="absolute top-4 right-4 z-20 flex flex-col gap-2">
				{/* Primary controls */}
				<div className="flex flex-col gap-1 p-2 bg-background/95 backdrop-blur-xl rounded-lg border shadow-xl">
					<ControlButton
						onClick={zoomIn}
						disabled={scale >= MAX_SCALE}
						title="Zoom in"
						shortcut="+"
					>
						<ZoomInIcon />
					</ControlButton>
					<ControlButton
						onClick={zoomOut}
						disabled={scale <= MIN_SCALE}
						title="Zoom out"
						shortcut="-"
					>
						<ZoomOutIcon />
					</ControlButton>
					<ControlButton
						onClick={zoomToFit}
						title="Fit to screen"
						shortcut="F"
					>
						<FitToScreenIcon />
					</ControlButton>
					<ControlButton
						onClick={resetZoom}
						title="Reset zoom"
						shortcut="0"
					>
						<ResetIcon />
					</ControlButton>
				</div>

				{/* Utility controls */}
				<div className="flex flex-col gap-1 p-2 bg-background/95 backdrop-blur-xl rounded-lg border shadow-xl">
					<ControlButton
						onClick={openInNewTab}
						title="Open in new tab"
						variant="primary"
						shortcut="Ctrl+N"
					>
						<NewTabIcon />
					</ControlButton>
					<ControlButton
						onClick={copySVG}
						title="Copy SVG"
						variant="secondary"
						shortcut="Ctrl+C"
					>
						<CopyIcon />
					</ControlButton>
					<ControlButton
						onClick={downloadSVG}
						title="Download SVG"
						variant="secondary"
					>
						<DownloadIcon />
					</ControlButton>
				</div>
			</div>

			{/* Enhanced Status Panel */}
			<div className="absolute top-4 left-4 z-20 flex flex-col gap-2">
				<div className="flex items-center gap-3 bg-background/95 backdrop-blur-xl rounded-lg px-3 py-2 border shadow-xl text-sm font-mono">
					<div className="flex items-center gap-2">
						<div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
						<span className="font-semibold">{Math.round(scale * 100)}%</span>
					</div>
				</div>
				{contentDimensions.width > 0 && (
					<div className="bg-background/95 backdrop-blur-xl rounded-lg px-3 py-2 border shadow-xl text-xs font-mono text-muted-foreground">
						{Math.round(contentDimensions.width)}×{Math.round(contentDimensions.height)}px
					</div>
				)}
				{isLoading && (
					<div className="bg-blue-500/10 backdrop-blur-xl rounded-lg px-3 py-2 border border-blue-500/20 shadow-xl text-xs text-blue-600 animate-pulse">
						Rendering...
					</div>
				)}
			</div>

			{/* Toast notifications */}
			{showTooltip === 'copied' && (
				<div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-30 bg-green-500 text-white px-4 py-2 rounded-lg shadow-xl animate-in fade-in duration-200">
					✓ SVG copied to clipboard
				</div>
			)}
			{showTooltip === 'downloaded' && (
				<div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-30 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-xl animate-in fade-in duration-200">
					✓ SVG downloaded
				</div>
			)}
			{showTooltip === 'opened' && (
				<div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-30 bg-purple-500 text-white px-4 py-2 rounded-lg shadow-xl animate-in fade-in duration-200">
					✓ Opened in new tab
				</div>
			)}
			{showTooltip === 'copy-error' && (
				<div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-30 bg-red-500 text-white px-4 py-2 rounded-lg shadow-xl animate-in fade-in duration-200">
					Failed to copy
				</div>
			)}

			{/* Main diagram container */}
			<div
				ref={containerRef}
				className="w-full h-96 overflow-hidden cursor-grab active:cursor-grabbing bg-gradient-to-br from-background via-muted/10 to-muted/20 relative"
				onWheel={handleWheel}
				onMouseDown={handleMouseDown}
				onMouseMove={handleMouseMove}
				onMouseUp={handleMouseUp}
				onMouseLeave={handleMouseUp}
				tabIndex={0}
				role="img"
				aria-label="Interactive Mermaid diagram"
			>
				{/* Loading overlay */}
				{isLoading && (
					<div className="absolute inset-0 z-10 flex items-center justify-center bg-background/80 backdrop-blur-sm">
						<div className="flex flex-col items-center gap-3">
							<div className="w-8 h-8 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
							<div className="text-sm text-muted-foreground">Rendering diagram...</div>
						</div>
					</div>
				)}

				{/* Diagram content */}
				<div
					ref={contentRef}
					style={transformStyle}
					className="w-full h-full flex items-center justify-center"
					dangerouslySetInnerHTML={{ __html: svg }}
				/>

				{/* Grid overlay for better visual reference */}
				{scale > 0.5 && (
					<div 
						className="absolute inset-0 opacity-5 pointer-events-none"
						style={{
							backgroundImage: `radial-gradient(circle at 1px 1px, currentColor 1px, transparent 0)`,
							backgroundSize: '20px 20px'
						}}
					/>
				)}
			</div>

			{/* Enhanced help panel */}
			<div className="absolute bottom-4 left-4 z-20 bg-background/95 backdrop-blur-xl rounded-lg px-3 py-2 border shadow-xl text-xs text-muted-foreground max-w-xs">
				<div className="flex items-center gap-2 mb-1">
					<div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
					<span className="font-semibold">Controls</span>
				</div>
				<div className="space-y-0.5 text-[11px]">
					<div>• <kbd className="px-1 bg-muted rounded text-[10px]">Mouse wheel</kbd> zoom</div>
					<div>• <kbd className="px-1 bg-muted rounded text-[10px]">Click & drag</kbd> pan</div>
					<div>• <kbd className="px-1 bg-muted rounded text-[10px]">F</kbd> fit screen</div>
					<div>• <kbd className="px-1 bg-muted rounded text-[10px]">+/-</kbd> zoom in/out</div>
				</div>
			</div>
		</div>
	);
}
