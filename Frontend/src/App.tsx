import React, { useState, useEffect, useRef } from 'react';
import { 
  Sparkles, ShoppingBag, Eye, Heart, RotateCcw, Sliders, Search, 
  ChevronRight, ArrowRight, Download, Share2, Check, Shield, Award, 
  Zap, Info, Sun, Moon, Compass, Filter, RefreshCw, Maximize2, 
  Layers, Palette, Scissors, CheckCircle2, Star, Play, Lock, ChevronDown,
  X, Grid, Image, Menu, User, HelpCircle, ExternalLink, Sparkle
} from 'lucide-react';
import * as THREE from 'three';

// --- MOCK CATALOG DATA ---
const MOCK_SAREES = [
  {
    id: 'saree-1',
    name: 'Burgundy Banarasi Silk',
    category: 'Banarasi',
    price: 34500,
    rating: 4.9,
    reviewsCount: 128,
    color: 'Burgundy',
    colorHex: '#621226',
    occasion: 'Wedding',
    fabric: 'Katan Pure Silk',
    borderType: 'Heavy Zari Brocade',
    blousePiece: 'Included (Unstitched brocade piece)',
    palluDetails: 'Intricate Floral Jaal with Kadwa Gold Weave',
    careInstructions: 'Dry Clean Only. Store in pure cotton cloth.',
    description: 'A timeless handwoven masterpiece crafted in Varanasi with dense gold zari kadwa weaving across deep burgundy Katan silk.',
    isNew: true,
    isFeatured: true,
    mainImage: 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&q=80&w=1000',
    tryOnImage: 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&q=80&w=1200', // Rendered mock result
    fabricTexture: 'https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?auto=format&fit=crop&q=80&w=600',
    swatches: ['#621226', '#8B0000', '#4A0E17']
  },
  {
    id: 'saree-2',
    name: 'Ivory Gold Kanjeevaram',
    category: 'Kanjeevaram',
    price: 48000,
    rating: 5.0,
    reviewsCount: 94,
    color: 'Ivory',
    colorHex: '#F3EFE0',
    occasion: 'Wedding',
    fabric: 'Mulberry Silk',
    borderType: 'Contrast Korvai Solid Gold Zari',
    blousePiece: 'Contrast Ruby Silk Blouse',
    palluDetails: 'Rich Temple Motif Heavy Zari Pallu',
    careInstructions: 'Dry Clean Only. Wrap in white muslin.',
    description: 'An iconic Kanchipuram weave boasting pristine warm ivory silk contrasted by pure 24k gold zari temple motifs.',
    isNew: false,
    isFeatured: true,
    mainImage: 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&q=80&w=1000',
    tryOnImage: 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&q=80&w=1200',
    fabricTexture: 'https://images.unsplash.com/photo-1609357605129-26f69add5d6e?auto=format&fit=crop&q=80&w=600',
    swatches: ['#F3EFE0', '#C5A059', '#E6DFCC']
  },
  {
    id: 'saree-3',
    name: 'Teal Temple Border Saree',
    category: 'Silk',
    price: 26500,
    rating: 4.8,
    reviewsCount: 67,
    color: 'Teal',
    colorHex: '#005F73',
    occasion: 'Festive',
    fabric: 'Tussar Handloom Silk',
    borderType: 'Ganga-Jamuna Temple Border',
    blousePiece: 'Running Silk Blouse with Border',
    palluDetails: 'Traditional Geometric Checks with Tassels',
    careInstructions: 'Dry Clean Only. Keep away from direct sunlight.',
    description: 'Sophisticated royal teal Tussar silk featuring vivid mustard & magenta double temple borders for festive elegance.',
    isNew: true,
    isFeatured: true,
    mainImage: 'https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?auto=format&fit=crop&q=80&w=1000',
    tryOnImage: 'https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?auto=format&fit=crop&q=80&w=1200',
    fabricTexture: 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&q=80&w=600',
    swatches: ['#005F73', '#0A9396', '#002930']
  },
  {
    id: 'saree-4',
    name: 'Rose Pink Chiffon Saree',
    category: 'Chiffon',
    price: 18900,
    rating: 4.7,
    reviewsCount: 52,
    color: 'Pink',
    colorHex: '#E8A598',
    occasion: 'Party Wear',
    fabric: 'Pure French Silk Chiffon',
    borderType: 'Hand Embroidered Gotta Patti',
    blousePiece: 'Custom Sequined Designer Blouse Fabric',
    palluDetails: 'Featherlight Sheer Pallu with Delicate Sequin Drops',
    careInstructions: 'Dry Clean Only. Soft fold storage.',
    description: 'Ethereal, light-as-air rose chiffon draped effortless with delicate hand-stitched gotta patti border shimmer.',
    isNew: false,
    isFeatured: false,
    mainImage: 'https://images.unsplash.com/photo-1609357605129-26f69add5d6e?auto=format&fit=crop&q=80&w=1000',
    tryOnImage: 'https://images.unsplash.com/photo-1609357605129-26f69add5d6e?auto=format&fit=crop&q=80&w=1200',
    fabricTexture: 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&q=80&w=600',
    swatches: ['#E8A598', '#F5E6E8', '#C97A6B']
  },
  {
    id: 'saree-5',
    name: 'Emerald Green Silk Saree',
    category: 'Silk',
    price: 38200,
    rating: 4.9,
    reviewsCount: 110,
    color: 'Green',
    colorHex: '#1B4332',
    occasion: 'Festive',
    fabric: 'Pure Raw Silk',
    borderType: 'Antiqued Gold Coin Motifs',
    blousePiece: 'Unstitched Deep Green Brocade',
    palluDetails: 'Rich Peacock Motif Zari Weave',
    careInstructions: 'Dry Clean Only.',
    description: 'A regal emerald green silk woven with antique golden coin motifs that emit a soft royal glow under light.',
    isNew: true,
    isFeatured: false,
    mainImage: 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&q=80&w=1000',
    tryOnImage: 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&q=80&w=1200',
    fabricTexture: 'https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?auto=format&fit=crop&q=80&w=600',
    swatches: ['#1B4332', '#2D6A4F', '#081C15']
  },
  {
    id: 'saree-6',
    name: 'Midnight Blue Designer Saree',
    category: 'Designer',
    price: 42000,
    rating: 4.8,
    reviewsCount: 88,
    color: 'Blue',
    colorHex: '#0B2545',
    occasion: 'Party Wear',
    fabric: 'Georgette Satin Blend',
    borderType: 'Crystal & Bead Hand Work',
    blousePiece: 'Heavy Embellished Blouse Piece',
    palluDetails: 'Cascading Sequin Stars Accent',
    careInstructions: 'Dry Clean Only. Steam gently.',
    description: 'A contemporary red-carpet ready midnight blue drape studded with delicate constellation sequins and crystal trimming.',
    isNew: false,
    isFeatured: true,
    mainImage: 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&q=80&w=1000',
    tryOnImage: 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&q=80&w=1200',
    fabricTexture: 'https://images.unsplash.com/photo-1609357605129-26f69add5d6e?auto=format&fit=crop&q=80&w=600',
    swatches: ['#0B2545', '#134074', '#030811']
  }
];

// FIXED SIGNATURE MODEL BASE IMAGE
const FIXED_SIGNATURE_MODEL_IMAGE = '/assets/model.png';

// --- REAL BACKEND API SERVICE ---
const vtoApi = {
  async getSarees() {
    const r = await fetch('/api/sarees');
    if (!r.ok) throw new Error('Failed to load sarees');
    return r.json();
  },
  async getSareeById(id) {
    const r = await fetch(`/api/sarees/${encodeURIComponent(id)}`);
    if (!r.ok) throw new Error('Failed to load saree');
    return r.json();
  },
  async submitTryOnJob(request) {
    const r = await fetch('/api/try-on', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({sareeId: request.sareeId}) });
    if (!r.ok) throw new Error(await r.text() || 'Failed to start virtual try-on');
    return r.json();
  },
  async checkJobStatus(jobId) {
    const r = await fetch(`/api/try-on/${encodeURIComponent(jobId)}`);
    if (!r.ok) throw new Error('Failed to check try-on status');
    return r.json();
  },
  async getGalleryItems() {
    const r = await fetch('/api/gallery');
    if (!r.ok) throw new Error('Failed to load gallery');
    return r.json();
  },
  async toggleFavourite(jobId) {
    const r = await fetch(`/api/gallery/${encodeURIComponent(jobId)}/favourite`, {method:'POST'});
    if (!r.ok) throw new Error('Failed to update favourite');
    return r.json();
  }
};

// --- 3D INTERACTIVE THREE.JS CANVAS FOR SAREE STUDIO & HERO ---
const Saree3DStudio = ({ sareeColor = '#621226', interactive = true, className = "h-72 w-full" }) => {
  const mountRef = useRef(null);

  useEffect(() => {
    const currentMount = mountRef.current;
    if (!currentMount) return;

    const width = currentMount.clientWidth || 300;
    const height = currentMount.clientHeight || 300;

    // 3D Scene setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 5;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    currentMount.appendChild(renderer.domElement);

    // Dynamic Saree Fabric Mesh Simulation (Parametric Waves)
    const geometry = new THREE.PlaneGeometry(3.5, 3.5, 32, 32);
    
    // Convert hex color string to THREE Color
    const themeColor = new THREE.Color(sareeColor);
    const material = new THREE.MeshStandardMaterial({
      color: themeColor,
      roughness: 0.35,
      metalness: 0.25,
      side: THREE.DoubleSide,
      wireframe: false
    });

    const fabricMesh = new THREE.Mesh(geometry, material);
    scene.add(fabricMesh);

    // Decorative Golden Particles Aura
    const particleCount = 120;
    const particleGeo = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount * 3; i += 3) {
      particlePositions[i] = (Math.random() - 0.5) * 6;
      particlePositions[i + 1] = (Math.random() - 0.5) * 6;
      particlePositions[i + 2] = (Math.random() - 0.5) * 4;
    }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));

    const particleMat = new THREE.PointsMaterial({
      color: new THREE.Color('#C5A059'),
      size: 0.04,
      transparent: true,
      opacity: 0.7
    });

    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    // Lighting Setup
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffd700, 1.2);
    dirLight.position.set(5, 5, 5);
    scene.add(dirLight);

    const pointLight = new THREE.PointLight(0xffffff, 0.8);
    pointLight.position.set(-5, -2, 2);
    scene.add(pointLight);

    // Mouse Interaction
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const handleMouseMove = (event) => {
      if (!interactive) return;
      const rect = currentMount.getBoundingClientRect();
      mouseX = ((event.clientX - rect.left) / width) * 2 - 1;
      mouseY = -((event.clientY - rect.top) / height) * 2 + 1;
    };

    if (interactive) {
      currentMount.addEventListener('mousemove', handleMouseMove);
    }

    // Animation Loop
    let animationFrameId;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      // Deform mesh geometry for flowing fabric wave effect
      const positionAttribute = geometry.attributes.position;
      for (let i = 0; i < positionAttribute.count; i++) {
        const u = positionAttribute.getX(i);
        const v = positionAttribute.getY(i);
        const z = Math.sin(u * 2 + elapsedTime * 1.5) * 0.2 + Math.cos(v * 2 + elapsedTime * 1.2) * 0.15;
        positionAttribute.setZ(i, z);
      }
      geometry.computeVertexNormals();
      positionAttribute.needsUpdate = true;

      // Smooth rotation dampening
      targetX += (mouseX - targetX) * 0.05;
      targetY += (mouseY - targetY) * 0.05;

      fabricMesh.rotation.y = elapsedTime * 0.2 + targetX * 0.8;
      fabricMesh.rotation.x = Math.sin(elapsedTime * 0.3) * 0.1 - targetY * 0.5;

      particles.rotation.y = elapsedTime * 0.05;

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!currentMount) return;
      const newW = currentMount.clientWidth;
      const newH = currentMount.clientHeight;
      camera.aspect = newW / newH;
      camera.updateProjectionMatrix();
      renderer.setSize(newW, newH);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      if (interactive && currentMount) {
        currentMount.removeEventListener('mousemove', handleMouseMove);
      }
      if (currentMount && renderer.domElement) {
        currentMount.removeChild(renderer.domElement);
      }
      geometry.dispose();
      material.dispose();
      particleGeo.dispose();
      particleMat.dispose();
      renderer.dispose();
    };
  }, [sareeColor, interactive]);

  return <div ref={mountRef} className={`relative overflow-hidden rounded-2xl cursor-grab active:cursor-grabbing ${className}`} />;
};

// --- BEFORE / AFTER INTERACTIVE SLIDER ---
const BeforeAfterSlider = ({ beforeImage, afterImage, labelBefore = "Base Signature Model", labelAfter = "Virtual Try-On Draped" }) => {
  const [sliderPos, setSliderPos] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef(null);

  const handleMove = (clientX) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    let percentage = (x / rect.width) * 100;
    if (percentage < 0) percentage = 0;
    if (percentage > 100) percentage = 100;
    setSliderPos(percentage);
  };

  const handleTouchMove = (e) => {
    if (isDragging) {
      handleMove(e.touches[0].clientX);
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      handleMove(e.clientX);
    }
  };

  useEffect(() => {
    const handleMouseUp = () => setIsDragging(false);
    window.addEventListener('mouseup', handleMouseUp);
    window.addEventListener('touchend', handleMouseUp);
    return () => {
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('touchend', handleMouseUp);
    };
  }, []);

  return (
    <div 
      ref={containerRef}
      className="relative w-full h-[500px] md:h-[620px] rounded-2xl overflow-hidden select-none shadow-2xl border border-[#C5A059]/20 group cursor-ew-resize bg-[#1A1A1A]"
      onMouseDown={() => setIsDragging(true)}
      onTouchStart={() => setIsDragging(true)}
      onMouseMove={handleMouseMove}
      onTouchMove={handleTouchMove}
    >
      {/* After Image (Full width background) */}
      <img 
        src={afterImage} 
        alt={labelAfter} 
        className="absolute inset-0 w-full h-full object-cover object-top"
      />
      <div className="absolute top-4 right-4 bg-[#1A1A1A]/80 backdrop-blur-md px-3 py-1.5 rounded-full border border-[#C5A059]/30 text-xs text-[#F3EFE0] font-sans tracking-wide">
        âœ¨ {labelAfter}
      </div>

      {/* Before Image (Clipped overlay) */}
      <div 
        className="absolute top-0 left-0 bottom-0 overflow-hidden"
        style={{ width: `${sliderPos}%` }}
      >
        <img 
          src={beforeImage} 
          alt={labelBefore} 
          className="absolute top-0 left-0 h-full max-w-none object-cover object-top"
          style={{ width: containerRef.current ? `${containerRef.current.clientWidth}px` : '100%' }}
        />
        <div className="absolute top-4 left-4 bg-[#1A1A1A]/80 backdrop-blur-md px-3 py-1.5 rounded-full border border-[#C5A059]/30 text-xs text-[#F3EFE0] font-sans tracking-wide">
          ðŸ‘¤ {labelBefore}
        </div>
      </div>

      {/* Slider Divider Line */}
      <div 
        className="absolute top-0 bottom-0 w-1 bg-[#C5A059] cursor-ew-resize shadow-[0_0_15px_#C5A059]"
        style={{ left: `${sliderPos}%` }}
      >
        <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-9 h-9 bg-[#1A1A1A] border-2 border-[#C5A059] rounded-full flex items-center justify-center shadow-lg text-[#C5A059]">
          <Sliders className="w-4 h-4" />
        </div>
      </div>
    </div>
  );
};

// --- NAVBAR COMPONENT ---
const Navbar = ({ activeTab, setActiveTab, favouritesCount, selectedSaree }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { id: 'home', label: 'Home' },
    { id: 'catalogue', label: 'Catalogue' },
    { id: 'tryon', label: 'Virtual Try-On', badge: selectedSaree ? 'Selected' : null },
    { id: 'gallery', label: 'Looks Gallery' }
  ];

  return (
    <nav className="sticky top-0 z-50 bg-[#FAF8F5]/90 backdrop-blur-md border-b border-[#C5A059]/20 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* Brand Logo */}
          <div 
            onClick={() => setActiveTab('home')}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#621226] to-[#1A1A1A] border border-[#C5A059] flex items-center justify-center text-[#C5A059] shadow-md group-hover:scale-105 transition-transform">
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <span className="font-serif text-2xl font-bold text-[#1A1A1A] tracking-wider block">
                DRAPE <span className="text-[#621226] italic font-light">AI</span>
              </span>
              <span className="text-[10px] uppercase tracking-widest text-[#C5A059] -mt-1 block font-sans">
                Signature Virtual Fitting
              </span>
            </div>
          </div>

          {/* Desktop Links */}
          <div className="hidden md:flex items-center gap-8 font-sans">
            {navLinks.map((link) => (
              <button
                key={link.id}
                onClick={() => setActiveTab(link.id)}
                className={`relative py-2 text-sm font-medium tracking-wider transition-colors uppercase ${
                  activeTab === link.id ? 'text-[#621226] font-semibold' : 'text-[#1A1A1A]/70 hover:text-[#621226]'
                }`}
              >
                {link.label}
                {link.badge && (
                  <span className="ml-2 px-2 py-0.5 text-[10px] bg-[#621226] text-white rounded-full font-sans tracking-normal">
                    {link.badge}
                  </span>
                )}
                {activeTab === link.id && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#C5A059] rounded-full" />
                )}
              </button>
            ))}
          </div>

          {/* Right Action Icons */}
          <div className="hidden md:flex items-center gap-4">
            <button 
              onClick={() => setActiveTab('gallery')}
              className="p-2 text-[#1A1A1A]/80 hover:text-[#621226] transition-colors relative"
              title="Saved Favourites"
            >
              <Heart className="w-5 h-5" />
              {favouritesCount > 0 && (
                <span className="absolute top-0 right-0 w-4 h-4 bg-[#621226] text-white rounded-full text-[10px] flex items-center justify-center font-bold">
                  {favouritesCount}
                </span>
              )}
            </button>
            <button 
              onClick={() => setActiveTab('tryon')}
              className="bg-gradient-to-r from-[#621226] to-[#4A0E17] text-[#FAF8F5] px-5 py-2.5 rounded-full border border-[#C5A059]/40 text-xs uppercase tracking-widest font-medium hover:shadow-lg transition-all flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4 text-[#C5A059]" />
              Enter Fitting Room
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-[#1A1A1A] hover:text-[#621226]"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-[#FAF8F5] border-b border-[#C5A059]/20 px-4 pt-2 pb-6 space-y-3 shadow-xl">
          {navLinks.map((link) => (
            <button
              key={link.id}
              onClick={() => {
                setActiveTab(link.id);
                setMobileMenuOpen(false);
              }}
              className={`block w-full text-left py-2 px-3 rounded-lg text-sm font-medium tracking-wider uppercase ${
                activeTab === link.id ? 'bg-[#621226] text-white' : 'text-[#1A1A1A]'
              }`}
            >
              {link.label}
            </button>
          ))}
          <button 
            onClick={() => {
              setActiveTab('tryon');
              setMobileMenuOpen(false);
            }}
            className="w-full bg-[#621226] text-white py-3 rounded-xl text-xs uppercase tracking-widest flex items-center justify-center gap-2 mt-4"
          >
            <Sparkles className="w-4 h-4 text-[#C5A059]" />
            Enter Fitting Room
          </button>
        </div>
      )}
    </nav>
  );
};

// --- PAGE 1: HOME PAGE COMPONENT ---
const HomePage = ({ onExplore, onTryOnSaree, sarees }) => {
  const featured = sarees.filter(s => s.isFeatured);

  return (
    <div className="space-y-24 pb-20">
      
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 lg:pt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            {/* Left Hero Content */}
            <div className="lg:col-span-7 space-y-8 text-center lg:text-left">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#F5E6E8] border border-[#621226]/20 text-[#621226] text-xs font-semibold uppercase tracking-widest">
                <Sparkles className="w-4 h-4 text-[#C5A059]" />
                Next-Gen Indian Luxury Fashion Tech
              </div>

              <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl font-bold text-[#1A1A1A] leading-tight">
                Find your perfect <br />
                <span className="italic font-light text-[#621226]">saree look</span> instantly.
              </h1>

              <p className="font-sans text-lg text-[#1A1A1A]/70 max-w-2xl mx-auto lg:mx-0 font-light leading-relaxed">
                Explore our handpicked royal saree collection and instantly preview each drape on our signature fixed model. Experience photorealistic zari sheen, fall, and border placement without step-by-step physical fitting.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start pt-2">
                <button
                  onClick={onExplore}
                  className="bg-[#621226] text-[#FAF8F5] px-8 py-4 rounded-full font-medium tracking-wider uppercase text-xs hover:bg-[#4A0E17] shadow-xl hover:shadow-2xl transition-all flex items-center justify-center gap-3 border border-[#C5A059]/40"
                >
                  Explore Sarees
                  <ArrowRight className="w-4 h-4 text-[#C5A059]" />
                </button>
                <a
                  href="#how-it-works"
                  className="bg-transparent text-[#1A1A1A] border border-[#1A1A1A]/20 px-8 py-4 rounded-full font-medium tracking-wider uppercase text-xs hover:border-[#621226] hover:text-[#621226] transition-all flex items-center justify-center gap-2"
                >
                  How It Works
                </a>
              </div>

              {/* Trust Metrics */}
              <div className="pt-8 border-t border-[#C5A059]/20 grid grid-cols-3 gap-4 text-center lg:text-left">
                <div>
                  <p className="font-serif text-2xl font-bold text-[#1A1A1A]">100%</p>
                  <p className="text-xs text-[#1A1A1A]/60 font-sans uppercase">Fixed Model Accuracy</p>
                </div>
                <div>
                  <p className="font-serif text-2xl font-bold text-[#1A1A1A]">4K</p>
                  <p className="text-xs text-[#1A1A1A]/60 font-sans uppercase">Fabric Texture Detail</p>
                </div>
                <div>
                  <p className="font-serif text-2xl font-bold text-[#1A1A1A]">&lt; 5s</p>
                  <p className="text-xs text-[#1A1A1A]/60 font-sans uppercase">Instant AI Draping</p>
                </div>
              </div>
            </div>

            {/* Right Hero Visual Mockup with 3D Canvas overlay */}
            <div className="lg:col-span-5 relative">
              <div className="relative mx-auto max-w-md lg:max-w-none">
                
                {/* Decorative Glowing Backdrop */}
                <div className="absolute -inset-4 bg-gradient-to-tr from-[#621226]/20 via-[#C5A059]/20 to-transparent rounded-3xl blur-2xl -z-10" />

                <div className="relative bg-[#FAF8F5] rounded-3xl p-3 border border-[#C5A059]/30 shadow-2xl overflow-hidden">
                  <div className="relative rounded-2xl overflow-hidden aspect-[3/4]">
                    <img 
                      src={FIXED_SIGNATURE_MODEL_IMAGE} 
                      alt="Drape AI Signature Model" 
                      className="w-full h-full object-cover object-top"
                    />
                    
                    {/* Floating Badge */}
                    <div className="absolute top-4 left-4 bg-[#1A1A1A]/85 backdrop-blur-md px-3 py-1.5 rounded-full border border-[#C5A059]/40 text-[11px] text-[#FAF8F5] flex items-center gap-2 font-sans">
                      <Shield className="w-3.5 h-3.5 text-[#C5A059]" />
                      Drape AI Signature Model
                    </div>

                    {/* Interactive 3D Fabric Inset Window */}
                    <div className="absolute bottom-4 left-4 right-4 bg-[#1A1A1A]/90 backdrop-blur-md p-3 rounded-xl border border-[#C5A059]/30 flex items-center justify-between text-white">
                      <div>
                        <p className="text-xs font-serif text-[#C5A059]">Interactive 3D Saree Fabric</p>
                        <p className="text-[11px] text-gray-300 font-sans">Move cursor to rotate drape aura</p>
                      </div>
                      <div className="w-16 h-16 rounded-lg overflow-hidden border border-[#C5A059]/40">
                        <Saree3DStudio sareeColor="#621226" className="w-full h-full" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* 3-Step How It Works Section */}
      <section id="how-it-works" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-3 mb-16">
          <span className="text-xs uppercase tracking-widest text-[#C5A059] font-semibold">Simplicity & Elegance</span>
          <h2 className="font-serif text-3xl sm:text-4xl font-bold text-[#1A1A1A]">How Drape AI Works</h2>
          <div className="w-16 h-0.5 bg-[#C5A059] mx-auto rounded-full" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              step: '01',
              title: 'Browse Saree Collection',
              desc: 'Explore curated Banarasi, Kanjeevaram, and Silk drapes from our master catalogue.',
              icon: Search
            },
            {
              step: '02',
              title: 'Select Favourite Design',
              desc: 'Review fabric weave, pallu details, matching blouse, and border specifications.',
              icon: Eye
            },
            {
              step: '03',
              title: 'Generate Virtual Try-On',
              desc: 'Click Try On to render the saree effortlessly onto our fixed signature model.',
              icon: Sparkles
            }
          ].map((item, idx) => (
            <div 
              key={idx}
              className="bg-white p-8 rounded-2xl border border-[#C5A059]/20 shadow-sm hover:shadow-md transition-shadow relative group"
            >
              <span className="font-serif text-5xl font-bold text-[#C5A059]/20 absolute top-6 right-6 group-hover:text-[#621226]/20 transition-colors">
                {item.step}
              </span>
              <div className="w-12 h-12 rounded-xl bg-[#F5E6E8] text-[#621226] flex items-center justify-center mb-6">
                <item.icon className="w-6 h-6" />
              </div>
              <h3 className="font-serif text-xl font-bold text-[#1A1A1A] mb-2">{item.title}</h3>
              <p className="text-sm text-[#1A1A1A]/70 font-sans leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Benefits Section */}
      <section className="bg-[#1A1A1A] text-[#FAF8F5] py-20 rounded-3xl mx-4 sm:mx-8 px-6 lg:px-12 border border-[#C5A059]/30 relative overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="text-center space-y-3 mb-16">
            <span className="text-xs uppercase tracking-widest text-[#C5A059] font-semibold">Unmatched Precision</span>
            <h2 className="font-serif text-3xl sm:text-4xl font-bold text-[#FAF8F5]">Why Use Drape AI?</h2>
            <p className="text-sm text-gray-400 font-sans">Engineered for luxury saree connoisseurs and effortless decision making</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { title: 'See Complete Drape', desc: 'Observe realistic pleat gathering, waist wraps, and graceful floor length fall.', icon: Layers },
              { title: 'Compare Colours & Styles', desc: 'Switch instantly between deep burgundy, ivory gold, and vibrant teal weaves.', icon: Palette },
              { title: 'Preview Complete Ensemble', desc: 'Review body fabric, border motifs, and pallu alignment combined harmoniously.', icon: Scissors },
              { title: 'Confident Decisions', desc: 'Eliminate guesswork prior to ordering bespoke or heavy handloom sarees.', icon: CheckCircle2 }
            ].map((card, i) => (
              <div key={i} className="bg-[#FAF8F5]/5 p-6 rounded-2xl border border-[#C5A059]/20 hover:border-[#C5A059] transition-colors">
                <card.icon className="w-8 h-8 text-[#C5A059] mb-4" />
                <h4 className="font-serif text-lg font-bold text-[#FAF8F5] mb-2">{card.title}</h4>
                <p className="text-xs text-gray-400 font-sans leading-relaxed">{card.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Sarees Carousel Preview */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-12">
          <div>
            <span className="text-xs uppercase tracking-widest text-[#C5A059] font-semibold">Handpicked Elegance</span>
            <h2 className="font-serif text-3xl font-bold text-[#1A1A1A]">Featured Sarees</h2>
          </div>
          <button 
            onClick={onExplore}
            className="text-xs uppercase tracking-widest text-[#621226] font-semibold flex items-center gap-2 hover:underline mt-4 sm:mt-0"
          >
            View Entire Catalogue ({sarees.length})
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {featured.map(saree => (
            <div key={saree.id} className="bg-white rounded-2xl overflow-hidden border border-[#C5A059]/20 shadow-md hover:shadow-xl transition-all group">
              <div className="relative aspect-[3/4] overflow-hidden bg-gray-100">
                <img 
                  src={saree.mainImage} 
                  alt={saree.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
                />
                <span className="absolute top-3 left-3 bg-[#621226] text-white text-[10px] uppercase font-bold tracking-wider px-2.5 py-1 rounded-md">
                  {saree.category}
                </span>
              </div>
              <div className="p-6 space-y-3">
                <div className="flex justify-between items-start">
                  <h3 className="font-serif text-lg font-bold text-[#1A1A1A]">{saree.name}</h3>
                  <span className="font-sans font-semibold text-sm text-[#621226]">â‚¹{saree.price.toLocaleString()}</span>
                </div>
                <p className="text-xs text-[#1A1A1A]/70 line-clamp-2">{saree.description}</p>
                <div className="pt-3 border-t border-gray-100 flex items-center gap-3">
                  <button 
                    onClick={() => onTryOnSaree(saree)}
                    className="flex-1 bg-[#621226] text-white py-2.5 rounded-xl text-xs uppercase tracking-wider font-semibold hover:bg-[#4A0E17] transition-colors flex items-center justify-center gap-2"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-[#C5A059]" />
                    Try On
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#1A1A1A] text-[#FAF8F5] border-t border-[#C5A059]/30 pt-16 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-10">
          <div className="space-y-4">
            <span className="font-serif text-2xl font-bold text-[#FAF8F5] tracking-wider block">
              DRAPE <span className="text-[#C5A059] italic font-light">AI</span>
            </span>
            <p className="text-xs text-gray-400 leading-relaxed font-sans">
              The premier virtual saree try-on destination. Revolutionizing Indian heritage fashion with fixed signature model intelligence.
            </p>
          </div>
          <div>
            <h4 className="font-serif text-sm font-bold text-[#C5A059] uppercase tracking-wider mb-4">Quick Navigation</h4>
            <ul className="space-y-2 text-xs text-gray-400 font-sans">
              <li><button onClick={onExplore} className="hover:text-white">Catalogue</button></li>
              <li><a href="#how-it-works" className="hover:text-white">How It Works</a></li>
              <li><button onClick={() => onTryOnSaree(sarees[0])} className="hover:text-white">Virtual Fitting Room</button></li>
            </ul>
          </div>
          <div>
            <h4 className="font-serif text-sm font-bold text-[#C5A059] uppercase tracking-wider mb-4">Help & Info</h4>
            <ul className="space-y-2 text-xs text-gray-400 font-sans">
              <li><a href="#" className="hover:text-white">Signature Model Specs</a></li>
              <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-white">Fabric Accuracy Guarantee</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-serif text-sm font-bold text-[#C5A059] uppercase tracking-wider mb-4">Connect</h4>
            <p className="text-xs text-gray-400 mb-4 font-sans">Follow our virtual fashion studio showcase.</p>
            <div className="flex gap-3 text-sm text-[#C5A059]">
              <span className="px-3 py-1 bg-white/5 rounded-full border border-[#C5A059]/20 text-xs">@DrapeAI</span>
            </div>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12 pt-6 border-t border-white/10 text-center text-xs text-gray-500 font-sans">
          Â© {new Date().getFullYear()} Drape AI Fitting Portal. All rights reserved. Powered by Python VTO Pipeline.
        </div>
      </footer>

    </div>
  );
};

// --- PAGE 2: CATALOGUE PAGE COMPONENT ---
const CataloguePage = ({ sarees, onSelectSaree, onTryOnSaree, favourites, toggleFavourite }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedOccasion, setSelectedOccasion] = useState('All');
  const [selectedColor, setSelectedColor] = useState('All');
  const [sortBy, setSortBy] = useState('featured');
  const [loading, setLoading] = useState(false);

  const categories = ['All', 'Silk', 'Banarasi', 'Kanjeevaram', 'Chiffon', 'Designer'];
  const occasions = ['All', 'Wedding', 'Festive', 'Party Wear'];
  const colors = ['All', 'Burgundy', 'Ivory', 'Teal', 'Pink', 'Green', 'Blue'];

  // Simulate skeleton load on filter change
  useEffect(() => {
    setLoading(true);
    const timer = setTimeout(() => setLoading(false), 250);
    return () => clearTimeout(timer);
  }, [searchTerm, selectedCategory, selectedOccasion, selectedColor, sortBy]);

  let filtered = sarees.filter(s => {
    if (selectedCategory !== 'All' && s.category !== selectedCategory) return false;
    if (selectedOccasion !== 'All' && s.occasion !== selectedOccasion) return false;
    if (selectedColor !== 'All' && s.color !== selectedColor) return false;
    if (searchTerm && !s.name.toLowerCase().includes(searchTerm.toLowerCase()) && !s.description.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  if (sortBy === 'price-asc') filtered.sort((a, b) => a.price - b.price);
  if (sortBy === 'price-desc') filtered.sort((a, b) => b.price - a.price);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-[#1A1A1A]">Saree Catalogue</h1>
        <p className="text-sm text-[#1A1A1A]/70 font-sans max-w-xl mx-auto">
          Explore master handlooms and modern drapes. Select any saree to preview instantly on our signature model.
        </p>
      </div>

      {/* Search & Sorting Controls Bar */}
      <div className="bg-white p-4 rounded-2xl border border-[#C5A059]/20 shadow-sm space-y-4 md:space-y-0 md:flex md:items-center md:justify-between gap-4">
        
        {/* Search Field */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input 
            type="text"
            placeholder="Search sarees by fabric, motif, or style..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 text-xs font-sans focus:outline-none focus:border-[#621226]"
          />
        </div>

        {/* Sort Selector */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-500 font-sans whitespace-nowrap">Sort By:</span>
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="py-2.5 px-3 bg-[#FAF8F5] border border-gray-200 rounded-xl text-xs font-sans text-[#1A1A1A] focus:outline-none focus:border-[#621226]"
          >
            <option value="featured">Featured</option>
            <option value="price-asc">Price: Low to High</option>
            <option value="price-desc">Price: High to Low</option>
          </select>
        </div>
      </div>

      {/* Filters Pills Grid */}
      <div className="space-y-3 bg-[#FAF8F5] p-5 rounded-2xl border border-[#C5A059]/20">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold text-[#621226] uppercase font-sans mr-2">Category:</span>
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-full text-xs font-sans transition-all ${
                selectedCategory === cat 
                  ? 'bg-[#621226] text-white font-semibold' 
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-gray-200/60">
          <span className="text-xs font-bold text-[#621226] uppercase font-sans mr-2">Occasion:</span>
          {occasions.map(occ => (
            <button
              key={occ}
              onClick={() => setSelectedOccasion(occ)}
              className={`px-3 py-1.5 rounded-full text-xs font-sans transition-all ${
                selectedOccasion === occ 
                  ? 'bg-[#621226] text-white font-semibold' 
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              {occ}
            </button>
          ))}
        </div>
      </div>

      {/* Saree Cards Grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {[1, 2, 3, 4, 5, 6].map(n => (
            <div key={n} className="bg-white rounded-2xl p-4 border border-gray-100 animate-pulse space-y-4">
              <div className="bg-gray-200 rounded-xl aspect-[3/4] w-full" />
              <div className="h-4 bg-gray-200 rounded w-3/4" />
              <div className="h-3 bg-gray-100 rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-gray-300 space-y-4">
          <Filter className="w-12 h-12 mx-auto text-gray-300" />
          <p className="font-serif text-lg font-semibold text-gray-700">No Sarees Found</p>
          <p className="text-xs text-gray-500 font-sans">Try clearing filters or adjusting your search term.</p>
          <button 
            onClick={() => {
              setSearchTerm('');
              setSelectedCategory('All');
              setSelectedOccasion('All');
              setSelectedColor('All');
            }}
            className="bg-[#621226] text-white text-xs px-5 py-2.5 rounded-full uppercase tracking-wider font-semibold"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {filtered.map(saree => {
            const isFav = favourites.some(f => f.id === saree.id);
            return (
              <div key={saree.id} className="bg-white rounded-2xl overflow-hidden border border-[#C5A059]/20 shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col group">
                
                {/* Saree Image Container */}
                <div className="relative aspect-[3/4] overflow-hidden bg-gray-100 cursor-pointer" onClick={() => onSelectSaree(saree)}>
                  <img 
                    src={saree.mainImage} 
                    alt={saree.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
                  />
                  
                  {/* Category Pill */}
                  <span className="absolute top-3 left-3 bg-[#1A1A1A]/80 backdrop-blur-md text-white text-[10px] uppercase font-bold tracking-wider px-2.5 py-1 rounded-md border border-white/20">
                    {saree.category}
                  </span>

                  {/* Favourite Button */}
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleFavourite(saree);
                    }}
                    className={`absolute top-3 right-3 p-2 rounded-full backdrop-blur-md transition-colors ${
                      isFav ? 'bg-[#621226] text-white' : 'bg-white/80 text-gray-700 hover:text-[#621226]'
                    }`}
                  >
                    <Heart className={`w-4 h-4 ${isFav ? 'fill-current' : ''}`} />
                  </button>
                </div>

                {/* Card Content */}
                <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                  <div>
                    <div className="flex justify-between items-start mb-1">
                      <h3 
                        onClick={() => onSelectSaree(saree)}
                        className="font-serif text-base font-bold text-[#1A1A1A] hover:text-[#621226] cursor-pointer transition-colors"
                      >
                        {saree.name}
                      </h3>
                      <span className="font-sans font-bold text-sm text-[#621226]">â‚¹{saree.price.toLocaleString()}</span>
                    </div>
                    <p className="text-xs text-gray-500 line-clamp-2 font-sans">{saree.description}</p>
                  </div>

                  {/* Swatches & Actions */}
                  <div className="space-y-3 pt-3 border-t border-gray-100">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5">
                        {saree.swatches.map((hex, i) => (
                          <span key={i} className="w-3.5 h-3.5 rounded-full border border-gray-300" style={{ backgroundColor: hex }} />
                        ))}
                      </div>
                      <span className="text-[11px] text-gray-400 font-sans">{saree.fabric}</span>
                    </div>

                    <div className="flex gap-2">
                      <button 
                        onClick={() => onSelectSaree(saree)}
                        className="flex-1 bg-gray-100 text-[#1A1A1A] py-2.5 rounded-xl text-xs uppercase tracking-wider font-semibold hover:bg-gray-200 transition-colors"
                      >
                        Details
                      </button>
                      <button 
                        onClick={() => onTryOnSaree(saree)}
                        className="flex-1 bg-[#621226] text-white py-2.5 rounded-xl text-xs uppercase tracking-wider font-semibold hover:bg-[#4A0E17] transition-colors flex items-center justify-center gap-1.5"
                      >
                        <Sparkles className="w-3.5 h-3.5 text-[#C5A059]" />
                        Try On
                      </button>
                    </div>
                  </div>

                </div>

              </div>
            );
          })}
        </div>
      )}

    </div>
  );
};

// --- PAGE 3: SAREE DETAILS PAGE COMPONENT ---
const SareeDetailsPage = ({ saree, onTryOn, onBack, favourites, toggleFavourite, allSarees }) => {
  const [selectedImage, setSelectedImage] = useState(saree.mainImage);
  const isFav = favourites.some(f => f.id === saree.id);

  const galleryImages = [
    saree.mainImage,
    saree.fabricTexture,
    saree.tryOnImage
  ];

  const related = allSarees.filter(s => s.id !== saree.id).slice(0, 3);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-16">
      
      {/* Back Button */}
      <button 
        onClick={onBack}
        className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-gray-600 hover:text-[#621226] transition-colors"
      >
        <ChevronRight className="w-4 h-4 rotate-180" />
        Back to Collection
      </button>

      {/* Main Details Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
        
        {/* Left Image Gallery */}
        <div className="lg:col-span-6 space-y-4">
          <div className="relative aspect-[3/4] rounded-2xl overflow-hidden bg-gray-100 border border-[#C5A059]/30 shadow-lg">
            <img 
              src={selectedImage} 
              alt={saree.name}
              className="w-full h-full object-cover object-top" 
            />
          </div>
          <div className="grid grid-cols-3 gap-3">
            {galleryImages.map((img, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedImage(img)}
                className={`aspect-square rounded-xl overflow-hidden border-2 transition-all ${
                  selectedImage === img ? 'border-[#621226] scale-95' : 'border-transparent opacity-70 hover:opacity-100'
                }`}
              >
                <img src={img} alt="Thumb" className="w-full h-full object-cover" />
              </button>
            ))}
          </div>
        </div>

        {/* Right Info Panel */}
        <div className="lg:col-span-6 space-y-6">
          <div>
            <span className="text-xs uppercase tracking-widest text-[#C5A059] font-bold block mb-1">
              {saree.category} Handloom
            </span>
            <h1 className="font-serif text-3xl sm:text-4xl font-bold text-[#1A1A1A]">{saree.name}</h1>
            <p className="font-sans text-2xl font-bold text-[#621226] mt-2">â‚¹{saree.price.toLocaleString()}</p>
          </div>

          <p className="text-sm text-gray-600 font-sans leading-relaxed">{saree.description}</p>

          {/* Try On Primary Action Card */}
          <div className="bg-[#FAF8F5] p-6 rounded-2xl border border-[#C5A059]/40 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-[#621226] text-[#C5A059] flex items-center justify-center">
                <Sparkles className="w-5 h-5 animate-pulse" />
              </div>
              <div>
                <h4 className="font-serif text-sm font-bold text-[#1A1A1A]">Ready for Virtual Try-On</h4>
                <p className="text-xs text-gray-500 font-sans">Preview drape instantly on our signature model</p>
              </div>
            </div>

            <div className="flex gap-3">
              <button 
                onClick={() => onTryOn(saree)}
                className="flex-1 bg-[#621226] text-white py-3.5 rounded-xl font-medium tracking-wider uppercase text-xs hover:bg-[#4A0E17] shadow-md transition-all flex items-center justify-center gap-2"
              >
                <Sparkles className="w-4 h-4 text-[#C5A059]" />
                Try This Saree on Model
              </button>
              <button 
                onClick={() => toggleFavourite(saree)}
                className={`p-3.5 rounded-xl border transition-colors ${
                  isFav ? 'bg-[#621226] text-white border-[#621226]' : 'bg-white text-gray-700 border-gray-300 hover:border-[#621226]'
                }`}
              >
                <Heart className={`w-5 h-5 ${isFav ? 'fill-current' : ''}`} />
              </button>
            </div>
          </div>

          {/* Breakdown Specs */}
          <div className="border-t border-b border-gray-200 py-6 space-y-4">
            <h3 className="font-serif text-base font-bold text-[#1A1A1A]">What the Try-On Includes</h3>
            <div className="grid grid-cols-2 gap-4 text-xs font-sans">
              <div className="bg-white p-3 rounded-xl border border-gray-100">
                <span className="text-gray-400 block font-semibold">Body Fabric</span>
                <span className="text-[#1A1A1A] font-medium">{saree.fabric}</span>
              </div>
              <div className="bg-white p-3 rounded-xl border border-gray-100">
                <span className="text-gray-400 block font-semibold">Border Motifs</span>
                <span className="text-[#1A1A1A] font-medium">{saree.borderType}</span>
              </div>
              <div className="bg-white p-3 rounded-xl border border-gray-100">
                <span className="text-gray-400 block font-semibold">Pallu Details</span>
                <span className="text-[#1A1A1A] font-medium">{saree.palluDetails}</span>
              </div>
              <div className="bg-white p-3 rounded-xl border border-gray-100">
                <span className="text-gray-400 block font-semibold">Blouse Piece</span>
                <span className="text-[#1A1A1A] font-medium">{saree.blousePiece}</span>
              </div>
            </div>
          </div>

          {/* Care Instructions */}
          <div className="space-y-2">
            <h4 className="font-serif text-xs font-bold text-gray-500 uppercase tracking-wider">Garment Care</h4>
            <p className="text-xs text-gray-600 font-sans">{saree.careInstructions}</p>
          </div>

        </div>
      </div>

      {/* Related Recommendations */}
      <div className="space-y-8 pt-12 border-t border-gray-200">
        <h2 className="font-serif text-2xl font-bold text-[#1A1A1A]">You May Also Like</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {related.map(item => (
            <div 
              key={item.id}
              onClick={() => onTryOn(item)}
              className="bg-white p-4 rounded-2xl border border-[#C5A059]/20 shadow-sm hover:shadow-md transition-all cursor-pointer flex gap-4 items-center"
            >
              <img src={item.mainImage} alt={item.name} className="w-20 h-24 object-cover rounded-xl" />
              <div>
                <h4 className="font-serif text-sm font-bold text-[#1A1A1A]">{item.name}</h4>
                <p className="text-xs text-[#621226] font-bold mt-1">â‚¹{item.price.toLocaleString()}</p>
                <span className="text-[10px] text-gray-400 block mt-2">Click to Try On</span>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};

// --- PAGE 4: MAIN VIRTUAL TRY-ON STUDIO PAGE ---
const TryOnPage = ({ selectedSaree, onBackToCatalogue, onSaveToGallery }) => {
  const [quality, setQuality] = useState('high'); // 'standard' | 'high'
  const [enhanceDetails, setEnhanceDetails] = useState(true);
  const [ambience, setAmbience] = useState('royal'); // 'daylight' | 'royal' | 'evening'
  
  // Generation State
  const [tryOnStatus, setTryOnStatus] = useState('idle'); // 'idle' | 'generating' | 'completed'
  const [progress, setProgress] = useState(0);
  const [currentStepText, setCurrentStepText] = useState('Preparing the saree');
  const [generatedResult, setGeneratedResult] = useState(null);

  // Friendly non-technical simulation steps
  const generationSteps = [
    { threshold: 15, text: 'Preparing the saree weave & texture...' },
    { threshold: 45, text: 'Styling the graceful pleats and drape...' },
    { threshold: 75, text: 'Aligning matching blouse & intricate border...' },
    { threshold: 95, text: 'Refining the final gold zari lighting...' }
  ];

  // Start real backend generation and poll the Python pipeline
  const handleGenerate = async () => {
    if (!selectedSaree) return;
    try {
      setTryOnStatus('generating');
      setProgress(5);
      setCurrentStepText(generationSteps[0].text);
      const job = await vtoApi.submitTryOnJob({ sareeId: selectedSaree.id, quality, enhanceFabricDetails: enhanceDetails });
      const started = Date.now();
      while (true) {
        const res = await vtoApi.checkJobStatus(job.jobId);
        if (res.status === 'completed') {
          setProgress(100);
          setCurrentStepText('Your virtual look is ready.');
          setGeneratedResult(res.imageUrl ? res.imageUrl : res.resultUrl);
          setTryOnStatus('completed');
          break;
        }
        if (res.status === 'failed') throw new Error(res.error || 'Virtual try-on failed');
        const elapsed = (Date.now() - started) / 1000;
        const p = Math.min(95, Math.max(8, Math.round(elapsed * 4)));
        setProgress(p);
        const matchedStep = generationSteps.slice().reverse().find(x => p >= x.threshold);
        if (matchedStep) setCurrentStepText(matchedStep.text);
        await new Promise(r => setTimeout(r, 1000));
      }
    } catch (error) {
      console.error(error);
      setTryOnStatus('idle');
      setProgress(0);
      alert(error instanceof Error ? error.message : 'Virtual try-on failed');
    }
  };

  const handleSave = () => {
    if (!generatedResult || !selectedSaree) return;
    const item = {
      id: `gal_${Date.now()}`,
      jobId: `local_${Date.now()}`,
      saree: selectedSaree,
      imageUrl: generatedResult,
      baseModelUrl: FIXED_SIGNATURE_MODEL_IMAGE,
      createdAt: new Date().toISOString(),
      isFavourite: true,
      quality
    };
    onSaveToGallery(item);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Fitting Room Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between bg-gradient-to-r from-[#1A1A1A] to-[#3A0A17] text-[#FAF8F5] p-6 rounded-3xl border border-[#C5A059]/40 gap-4">
        <div>
          <span className="text-[10px] uppercase tracking-widest text-[#C5A059] font-bold block mb-1">
            Drape AI Signature Virtual Studio
          </span>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold">Virtual Fitting Room</h1>
          <p className="text-xs text-gray-300 font-sans mt-1">Fixed signature model architecture with dynamic silk simulation.</p>
        </div>
        <button 
          onClick={onBackToCatalogue}
          className="self-start md:self-auto px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-full text-xs font-sans uppercase tracking-wider border border-white/20 transition-colors"
        >
          Change Saree
        </button>
      </div>

      {/* Main Studio 3-Panel Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* LEFT PANEL: Selected Saree Summary */}
        <div className="lg:col-span-3 bg-white p-6 rounded-2xl border border-[#C5A059]/20 shadow-sm space-y-6">
          <h3 className="font-serif text-base font-bold text-[#1A1A1A] border-b pb-3">Selected Saree</h3>

          {selectedSaree ? (
            <div className="space-y-4">
              <div className="aspect-[3/4] rounded-xl overflow-hidden bg-gray-100 border border-gray-200">
                <img src={selectedSaree.mainImage} alt={selectedSaree.name} className="w-full h-full object-cover" />
              </div>
              <div>
                <h4 className="font-serif text-lg font-bold text-[#1A1A1A]">{selectedSaree.name}</h4>
                <p className="text-xs text-[#621226] font-bold font-sans">â‚¹{selectedSaree.price.toLocaleString()}</p>
                <span className="inline-block mt-2 px-2.5 py-0.5 bg-[#F5E6E8] text-[#621226] text-[10px] uppercase font-bold rounded-md">
                  {selectedSaree.category}
                </span>
              </div>

              {/* Draping Feature Highlights */}
              <div className="space-y-2 pt-3 border-t border-gray-100 text-xs text-gray-600 font-sans">
                <div className="flex items-center gap-2">
                  <Check className="w-3.5 h-3.5 text-[#C5A059]" />
                  <span>Full floor-length drape</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-3.5 h-3.5 text-[#C5A059]" />
                  <span>Matching blouse fitting</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-3.5 h-3.5 text-[#C5A059]" />
                  <span>Border & pallu alignment</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-10 space-y-3">
              <p className="text-xs text-gray-500 font-sans">No saree selected yet.</p>
              <button 
                onClick={onBackToCatalogue}
                className="bg-[#621226] text-white px-4 py-2 rounded-xl text-xs uppercase tracking-wider font-semibold"
              >
                Select Saree
              </button>
            </div>
          )}
        </div>

        {/* CENTER CANVAS AREA: Base Model & Draped Before/After Studio */}
        <div className="lg:col-span-6 space-y-4">
          
          {/* Studio Ambience Controls */}
          <div className="flex items-center justify-between bg-white px-4 py-2.5 rounded-xl border border-gray-200 text-xs font-sans">
            <span className="text-gray-500 font-medium">Lighting Ambience:</span>
            <div className="flex gap-2">
              {[
                { id: 'royal', label: 'Royal Studio' },
                { id: 'daylight', label: 'Natural Daylight' },
                { id: 'evening', label: 'Evening Gala' }
              ].map(a => (
                <button
                  key={a.id}
                  onClick={() => setAmbience(a.id)}
                  className={`px-3 py-1 rounded-lg transition-all ${
                    ambience === a.id ? 'bg-[#1A1A1A] text-[#C5A059] font-bold' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {a.label}
                </button>
              ))}
            </div>
          </div>

          {/* Main Visual Display Area */}
          <div className="relative rounded-2xl overflow-hidden bg-[#1A1A1A] min-h-[500px] md:min-h-[620px] flex items-center justify-center border border-[#C5A059]/30 shadow-2xl">
            
            {/* IDLE STATE: Display Base Model */}
            {tryOnStatus === 'idle' && (
              <div className="relative w-full h-full">
                <img 
                  src={FIXED_SIGNATURE_MODEL_IMAGE} 
                  alt="Drape AI Signature Model" 
                  className="w-full h-full object-cover object-top"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/20 flex flex-col justify-end p-8 text-white space-y-3">
                  <div className="inline-flex items-center gap-2 bg-[#1A1A1A]/80 backdrop-blur-md px-3 py-1.5 rounded-full border border-[#C5A059]/40 w-fit text-xs text-[#C5A059]">
                    <Shield className="w-3.5 h-3.5" />
                    Drape AI Fixed Signature Model
                  </div>
                  <p className="font-serif text-xl sm:text-2xl font-bold">
                    Click â€œGenerate Lookâ€ to try on <br />
                    <span className="text-[#C5A059] italic">{selectedSaree?.name || 'selected saree'}</span>
                  </p>
                </div>
              </div>
            )}

            {/* GENERATING STATE: Shimmering Fabric Progress Simulation */}
            {tryOnStatus === 'generating' && (
              <div className="w-full h-full flex flex-col items-center justify-center p-8 text-center space-y-8 bg-gradient-to-b from-[#1A1A1A] to-[#2D0A14] text-white">
                
                {/* Dynamic 3D Shimmer Aura */}
                <div className="w-48 h-48 rounded-2xl overflow-hidden border border-[#C5A059]/50 shadow-[0_0_30px_rgba(197,160,89,0.3)]">
                  <Saree3DStudio sareeColor={selectedSaree?.colorHex || '#621226'} className="w-full h-full" />
                </div>

                <div className="space-y-4 max-w-md w-full">
                  <span className="text-xs font-serif uppercase tracking-widest text-[#C5A059] animate-pulse">
                    AI Virtual Fitting Pipeline
                  </span>
                  
                  <p className="font-serif text-lg font-semibold text-white">{currentStepText}</p>

                  {/* Progress Bar */}
                  <div className="w-full bg-white/10 rounded-full h-2.5 overflow-hidden border border-white/20">
                    <div 
                      className="bg-gradient-to-r from-[#C5A059] to-[#E8A598] h-full transition-all duration-300 rounded-full"
                      style={{ width: `${progress}%` }}
                    />
                  </div>

                  <span className="text-xs font-sans text-gray-400 block">{progress}% Completed</span>
                </div>
              </div>
            )}

            {/* COMPLETED STATE: Interactive Before / After Slider */}
            {tryOnStatus === 'completed' && generatedResult && (
              <BeforeAfterSlider 
                beforeImage={FIXED_SIGNATURE_MODEL_IMAGE}
                afterImage={generatedResult}
                labelBefore="Signature Base Model"
                labelAfter={`${selectedSaree?.name || 'Saree'} Virtual Try-On`}
              />
            )}

          </div>

        </div>

        {/* RIGHT PANEL: Generation Controls & Post Actions */}
        <div className="lg:col-span-3 bg-white p-6 rounded-2xl border border-[#C5A059]/20 shadow-sm space-y-6">
          <h3 className="font-serif text-base font-bold text-[#1A1A1A] border-b pb-3">Your Selected Look</h3>

          {/* Quality Mode Toggle */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-600 font-sans block">Quality Mode</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setQuality('standard')}
                className={`py-2 rounded-xl text-xs font-sans transition-all border ${
                  quality === 'standard' ? 'bg-[#621226] text-white border-[#621226]' : 'bg-gray-50 text-gray-700 border-gray-200'
                }`}
              >
                Standard
              </button>
              <button
                onClick={() => setQuality('high')}
                className={`py-2 rounded-xl text-xs font-sans transition-all border ${
                  quality === 'high' ? 'bg-[#621226] text-white border-[#621226]' : 'bg-gray-50 text-gray-700 border-gray-200'
                }`}
              >
                High Quality
              </button>
            </div>
          </div>

          {/* Enhance Fabric Details Toggle */}
          <div className="flex items-center justify-between pt-2 border-t border-gray-100">
            <div>
              <span className="text-xs font-semibold text-gray-700 font-sans block">Enhance Fabric Detail</span>
              <span className="text-[10px] text-gray-400 font-sans">Highlight gold zari shimmer</span>
            </div>
            <input 
              type="checkbox"
              checked={enhanceDetails}
              onChange={(e) => setEnhanceDetails(e.target.checked)}
              className="w-4 h-4 accent-[#621226] rounded cursor-pointer"
            />
          </div>

          {/* Primary CTA Button */}
          <button
            disabled={!selectedSaree || tryOnStatus === 'generating'}
            onClick={handleGenerate}
            className={`w-full py-4 rounded-xl text-xs uppercase tracking-widest font-bold transition-all shadow-lg flex items-center justify-center gap-2 ${
              !selectedSaree || tryOnStatus === 'generating'
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-[#621226] to-[#4A0E17] text-[#FAF8F5] hover:opacity-95'
            }`}
          >
            <Sparkles className="w-4 h-4 text-[#C5A059]" />
            {tryOnStatus === 'completed' ? 'Regenerate Look' : 'Generate Look'}
          </button>

          {/* Post-Generation Actions */}
          {tryOnStatus === 'completed' && (
            <div className="space-y-3 pt-4 border-t border-gray-200 animate-fade-in">
              <button 
                onClick={handleSave}
                className="w-full bg-[#FAF8F5] border border-[#C5A059] text-[#1A1A1A] py-2.5 rounded-xl text-xs uppercase tracking-wider font-semibold hover:bg-[#621226] hover:text-white transition-colors flex items-center justify-center gap-2"
              >
                <Heart className="w-4 h-4 text-[#C5A059]" />
                Save to Gallery
              </button>
              
              <button 
                onClick={onBackToCatalogue}
                className="w-full text-xs text-gray-500 font-sans hover:underline text-center block pt-2"
              >
                Try Another Saree
              </button>
            </div>
          )}

        </div>

      </div>

    </div>
  );
};

// --- PAGE 5: LOOKS GALLERY PAGE & LIGHTBOX COMPONENT ---
const LooksGalleryPage = ({ galleryItems, onTryOnAgain }) => {
  const [activeFilter, setActiveFilter] = useState('All');
  const [selectedItemModal, setSelectedItemModal] = useState(null);

  const filtered = galleryItems.filter(item => {
    if (activeFilter === 'Favourites') return item.isFavourite;
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-serif text-3xl font-bold text-[#1A1A1A]">Saved Looks Gallery</h1>
          <p className="text-xs text-gray-500 font-sans mt-1">Your rendered virtual fitting room previews</p>
        </div>

        {/* Filters */}
        <div className="flex gap-2 bg-[#FAF8F5] p-1.5 rounded-xl border border-gray-200 w-fit">
          {['All Looks', 'Favourites'].map(f => (
            <button
              key={f}
              onClick={() => setActiveFilter(f.startsWith('All') ? 'All' : 'Favourites')}
              className={`px-4 py-2 rounded-lg text-xs font-sans transition-all ${
                (activeFilter === 'All' && f.startsWith('All')) || (activeFilter === 'Favourites' && f === 'Favourites')
                  ? 'bg-[#621226] text-white font-semibold'
                  : 'text-gray-600 hover:text-[#1A1A1A]'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Grid */}
      {filtered.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-gray-300 space-y-4">
          <Image className="w-12 h-12 mx-auto text-gray-300" />
          <p className="font-serif text-lg font-semibold text-gray-700">No Saved Looks Yet</p>
          <p className="text-xs text-gray-500 font-sans max-w-sm mx-auto">
            Generate virtual try-ons from the catalogue to save and compare your looks here.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {filtered.map(item => (
            <div 
              key={item.id}
              onClick={() => setSelectedItemModal(item)}
              className="bg-white rounded-2xl overflow-hidden border border-[#C5A059]/20 shadow-sm hover:shadow-xl transition-all cursor-pointer group"
            >
              <div className="relative aspect-[3/4] overflow-hidden bg-gray-100">
                <img src={item.imageUrl} alt={item.saree.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                <div className="absolute top-3 right-3 bg-[#1A1A1A]/80 backdrop-blur-md p-2 rounded-full text-[#C5A059]">
                  <Sparkles className="w-4 h-4" />
                </div>
              </div>

              <div className="p-5 flex justify-between items-center">
                <div>
                  <h3 className="font-serif text-base font-bold text-[#1A1A1A]">{item.saree.name}</h3>
                  <p className="text-[11px] text-gray-400 font-sans mt-0.5">
                    Rendered {new Date(item.createdAt).toLocaleDateString()}
                  </p>
                </div>
                <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-[#621226] group-hover:translate-x-1 transition-all" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* DETAIL LIGHTBOX MODAL */}
      {selectedItemModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-[#FAF8F5] rounded-3xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-[#C5A059]/40 p-6 space-y-6 relative">
            
            <button 
              onClick={() => setSelectedItemModal(null)}
              className="absolute top-6 right-6 p-2 rounded-full bg-gray-200 text-gray-700 hover:bg-[#621226] hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <h2 className="font-serif text-2xl font-bold text-[#1A1A1A]">{selectedItemModal.saree.name} Look</h2>

            <BeforeAfterSlider 
              beforeImage={selectedItemModal.baseModelUrl}
              afterImage={selectedItemModal.imageUrl}
            />

            <div className="flex flex-col sm:flex-row justify-between items-center gap-4 pt-4 border-t border-gray-200">
              <div className="text-xs text-gray-500 font-sans">
                Fabric: <span className="font-bold text-[#1A1A1A]">{selectedItemModal.saree.fabric}</span> | Price: <span className="font-bold text-[#621226]">â‚¹{selectedItemModal.saree.price.toLocaleString()}</span>
              </div>
              <button 
                onClick={() => {
                  onTryOnAgain(selectedItemModal.saree);
                  setSelectedItemModal(null);
                }}
                className="bg-[#621226] text-white px-6 py-3 rounded-xl text-xs uppercase tracking-wider font-semibold hover:bg-[#4A0E17]"
              >
                Try This Saree Again
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};

// --- MAIN APP ENTRY CONTAINER ---
export default function App() {
  const [activeTab, setActiveTab] = useState('home'); // 'home' | 'catalogue' | 'details' | 'tryon' | 'gallery'
  const [sarees, setSarees] = useState<any[]>([]);
  const [selectedSaree, setSelectedSaree] = useState<any | null>(null);
  const [favourites, setFavourites] = useState<any[]>([]);
  const [galleryItems, setGalleryItems] = useState([]);

  useEffect(() => {
    Promise.all([vtoApi.getSarees(), vtoApi.getGalleryItems()])
      .then(([items, gallery]) => {
        const normalized = items.map(s => ({
  ...s,
  rating: 4.9,
  reviewsCount: 0,
  colorHex: '#621226',
  borderType: 'Traditional woven border',
  blousePiece: 'Included',
  palluDetails: 'Traditional detailed pallu',
  careInstructions: s.care,
  isNew: false,
  isFeatured: true,

  // PRODUCT IMAGE â€” NOT THE FIXED MODEL
  mainImage: '/sarees/s1.png',

  // Keep model only for the actual VTO base model
  fabricTexture: '/sarees/s1.jpg',

  swatches: ['#621226']
}));        setSarees(normalized);
        setSelectedSaree(normalized[0] || null);
        setGalleryItems(gallery);
      })
      .catch(err => console.error('Backend load failed:', err));
  }, []);


  const toggleFavourite = (saree) => {
    setFavourites(prev => {
      const exists = prev.some(f => f.id === saree.id);
      if (exists) return prev.filter(f => f.id !== saree.id);
      return [...prev, saree];
    });
  };

  const handleSelectSareeForDetails = (saree) => {
    setSelectedSaree(saree);
    setActiveTab('details');
  };

  const handleTryOnSaree = (saree) => {
    setSelectedSaree(saree);
    setActiveTab('tryon');
  };

  const handleSaveToGallery = (item) => {
    setGalleryItems(prev => [item, ...prev]);
    setActiveTab('gallery');
  };

  return (
    <div className="min-h-screen bg-[#FAF8F5] text-[#1A1A1A] font-sans selection:bg-[#621226] selection:text-white flex flex-col">
      
      {/* Navigation Header */}
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        favouritesCount={favourites.length}
        selectedSaree={selectedSaree}
      />

      {/* Dynamic View Page Routing */}
      <main className="flex-1">
        {activeTab === 'home' && (
          <HomePage 
            sarees={sarees}
            onExplore={() => setActiveTab('catalogue')}
            onTryOnSaree={handleTryOnSaree}
          />
        )}

        {activeTab === 'catalogue' && (
          <CataloguePage 
            sarees={sarees}
            onSelectSaree={handleSelectSareeForDetails}
            onTryOnSaree={handleTryOnSaree}
            favourites={favourites}
            toggleFavourite={toggleFavourite}
          />
        )}

        {activeTab === 'details' && selectedSaree && (
          <SareeDetailsPage 
            saree={selectedSaree}
            allSarees={sarees}
            onTryOn={handleTryOnSaree}
            onBack={() => setActiveTab('catalogue')}
            favourites={favourites}
            toggleFavourite={toggleFavourite}
          />
        )}

        {activeTab === 'tryon' && (
          <TryOnPage 
            selectedSaree={selectedSaree}
            onBackToCatalogue={() => setActiveTab('catalogue')}
            onSaveToGallery={handleSaveToGallery}
          />
        )}

        {activeTab === 'gallery' && (
          <LooksGalleryPage 
            galleryItems={galleryItems}
            onTryOnAgain={handleTryOnSaree}
          />
        )}
      </main>

    </div>
  );
}
