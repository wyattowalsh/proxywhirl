"use client";

import { useEffect, useId, useRef, useState, useCallback } from "react";
import { useTheme } from "next-themes";

export function Mermaid({ chart }: { chart: string }) {
	const id = useId();
	const [svg, setSvg] = useState("");
	const containerRef = useRef<HTMLDivElement>(null);
	const contentRef = useRef<HTMLDivElement>(null);
	const currentChartRef = useRef<string>(null);
	const { resolvedTheme } = useTheme();
	
	// Zoom and pan state
	const [scale, setScale] = useState(1);
	const [position, setPosition] = useState({ x: 0, y: 0 });
	const [isDragging, setIsDragging] = useState(false);
	const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
	const [dragStartPosition, setDragStartPosition] = useState({ x: 0, y: 0 });
	const [contentDimensions, setContentDimensions] = useState({ width: 0, height: 0 });

	const MIN_SCALE = 0.1;
	const MAX_SCALE = 5;
	const ZOOM_STEP = 0.1;
	const CONTAINER_PADDING = 20; // Padding for zoom to fit

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
			const { default: mermaid } = await import("mermaid");

			try {
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
				}, 100); // Small delay to ensure container is rendered
			} catch (error) {
				console.error("Error while rendering mermaid", error);
			}
		}

		void renderChart();
	}, [chart, id, resolvedTheme, calculateZoomToFit]);

	// Handle mouse wheel zoom
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

	// Zoom controls
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

	// Open in new tab
	const openInNewTab = () => {
		const newWindow = window.open('', '_blank');
		if (newWindow) {
			const htmlContent = `
<!DOCTYPE html>
<html>
<head>
	<title>Mermaid Diagram</title>
	<meta charset="utf-8">
	<style>
		body {
			margin: 0;
			padding: 20px;
			font-family: system-ui, -apple-system, sans-serif;
			background: ${resolvedTheme === 'dark' ? '#0a0a0a' : '#ffffff'};
			color: ${resolvedTheme === 'dark' ? '#ffffff' : '#000000'};
			display: flex;
			justify-content: center;
			align-items: center;
			min-height: 100vh;
		}
		.diagram-container {
			max-width: 100%;
			max-height: 100%;
			overflow: auto;
		}
	</style>
</head>
<body>
	<div class="diagram-container">
		${svg}
	</div>
</body>
</html>`;
			newWindow.document.write(htmlContent);
			newWindow.document.close();
		}
	};

	// Transform style
	const transformStyle = {
		transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
		transformOrigin: "center center",
		transition: isDragging ? "none" : "transform 0.1s ease",
	};

	return (
		<div className="relative border rounded-lg overflow-hidden bg-background">
			{/* Zoom Controls */}
			<div className="absolute top-2 right-2 z-10 flex flex-col gap-1 bg-background/80 backdrop-blur rounded-md p-1 border">
				<button
					onClick={zoomIn}
					disabled={scale >= MAX_SCALE}
					className="w-8 h-8 flex items-center justify-center text-xs font-mono bg-muted hover:bg-muted/80 disabled:opacity-50 disabled:cursor-not-allowed rounded border"
					title="Zoom in"
				>
					+
				</button>
				<button
					onClick={zoomOut}
					disabled={scale <= MIN_SCALE}
					className="w-8 h-8 flex items-center justify-center text-xs font-mono bg-muted hover:bg-muted/80 disabled:opacity-50 disabled:cursor-not-allowed rounded border"
					title="Zoom out"
				>
					−
				</button>
				<button
					onClick={zoomToFit}
					className="w-8 h-8 flex items-center justify-center text-xs font-mono bg-muted hover:bg-muted/80 rounded border"
					title="Zoom to fit"
				>
					⊞
				</button>
				<button
					onClick={resetZoom}
					className="w-8 h-8 flex items-center justify-center text-xs font-mono bg-muted hover:bg-muted/80 rounded border"
					title="Reset zoom (100%)"
				>
					⌂
				</button>
				<div className="w-full h-px bg-border my-1" />
				<button
					onClick={openInNewTab}
					className="w-8 h-8 flex items-center justify-center text-xs font-mono bg-muted hover:bg-muted/80 rounded border"
					title="Open in new tab"
				>
					↗
				</button>
			</div>

			{/* Zoom indicator */}
			<div className="absolute top-2 left-2 z-10 bg-background/80 backdrop-blur rounded-md px-2 py-1 border text-xs font-mono">
				{Math.round(scale * 100)}%
			</div>

			{/* Dimensions indicator */}
			{contentDimensions.width > 0 && (
				<div className="absolute top-2 left-20 z-10 bg-background/80 backdrop-blur rounded-md px-2 py-1 border text-xs font-mono text-muted-foreground">
					{Math.round(contentDimensions.width)}×{Math.round(contentDimensions.height)}
				</div>
			)}

			{/* Container for the diagram */}
			<div
				ref={containerRef}
				className="w-full h-96 overflow-hidden cursor-grab active:cursor-grabbing"
				onWheel={handleWheel}
				onMouseDown={handleMouseDown}
				onMouseMove={handleMouseMove}
				onMouseUp={handleMouseUp}
				onMouseLeave={handleMouseUp}
			>
				<div
					ref={contentRef}
					style={transformStyle}
					className="w-full h-full flex items-center justify-center"
					dangerouslySetInnerHTML={{ __html: svg }}
				/>
			</div>

			{/* Help text */}
			<div className="absolute bottom-2 left-2 z-10 bg-background/80 backdrop-blur rounded-md px-2 py-1 border text-xs text-muted-foreground">
				Mouse wheel: zoom • Drag: pan • ⊞: fit
			</div>
		</div>
	);
}
