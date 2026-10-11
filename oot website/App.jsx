import React, { useState } from 'react';
import { Play, Info, Search, Bell, User, Lock, Mail, Film, Plus } from 'lucide-react';

export default function App() {
  const [currentPage, setCurrentPage] = useState('login'); // 'login' | 'signup' | 'home'
  const [formData, setFormData] = useState({ email: '', password: '', name: '' });

  const handleAuthSubmit = (e) => {
    e.preventDefault();
    // Auth success ke baad homepage par redirect
    setCurrentPage('home');
  };

  // --- 1. LOGIN PAGE ---
  if (currentPage === 'login') {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex flex-col justify-between p-6 bg-cover bg-center relative" style={{ backgroundImage: 'linear-gradient(to bottom, rgba(0,0,0,0.8), rgba(0,0,0,0.9)), url("https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?auto=format&fit=crop&q=80")' }}>
        <div className="flex justify-between items-center max-w-6xl mx-auto w-full">
          <h1 className="text-3xl font-bold text-red-600 tracking-wider">STREAMFLIX</h1>
        </div>

        <div className="max-w-md w-full mx-auto bg-black/75 p-8 rounded-xl backdrop-blur-md border border-slate-800 shadow-2xl">
          <h2 className="text-3xl font-bold mb-6 text-center">Sign In</h2>
          <form onSubmit={handleAuthSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-1">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 text-slate-500 w-5 h-5" />
                <input 
                  type="email" 
                  required
                  placeholder="name@example.com"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2.5 pl-10 pr-4 text-white focus:outline-none focus:border-red-600"
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-slate-400 mb-1">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 text-slate-500 w-5 h-5" />
                <input 
                  type="password" 
                  required
                  placeholder="••••••••"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2.5 pl-10 pr-4 text-white focus:outline-none focus:border-red-600"
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                />
              </div>
            </div>

            <button type="submit" className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 rounded-lg mt-4 transition">
              Sign In
            </button>
          </form>

          <p className="mt-6 text-center text-slate-400 text-sm">
            New to Streamflix?{' '}
            <button onClick={() => setCurrentPage('signup')} className="text-white hover:underline font-medium">
              Sign up now
            </button>
          </p>
        </div>

        <p className="text-center text-xs text-slate-500">© 2026 Streamflix. All rights reserved.</p>
      </div>
    );
  }

  // --- 2. SIGNUP PAGE ---
  if (currentPage === 'signup') {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex flex-col justify-between p-6 bg-cover bg-center relative" style={{ backgroundImage: 'linear-gradient(to bottom, rgba(0,0,0,0.8), rgba(0,0,0,0.9)), url("https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?auto=format&fit=crop&q=80")' }}>
        <div className="flex justify-between items-center max-w-6xl mx-auto w-full">
          <h1 className="text-3xl font-bold text-red-600 tracking-wider">STREAMFLIX</h1>
        </div>

        <div className="max-w-md w-full mx-auto bg-black/75 p-8 rounded-xl backdrop-blur-md border border-slate-800 shadow-2xl">
          <h2 className="text-3xl font-bold mb-6 text-center">Create Account</h2>
          <form onSubmit={handleAuthSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-1">Full Name</label>
              <div className="relative">
                <User className="absolute left-3 top-3 text-slate-500 w-5 h-5" />
                <input 
                  type="text" 
                  required
                  placeholder="John Doe"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2.5 pl-10 pr-4 text-white focus:outline-none focus:border-red-600"
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-slate-400 mb-1">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 text-slate-500 w-5 h-5" />
                <input 
                  type="email" 
                  required
                  placeholder="name@example.com"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2.5 pl-10 pr-4 text-white focus:outline-none focus:border-red-600"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-slate-400 mb-1">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 text-slate-500 w-5 h-5" />
                <input 
                  type="password" 
                  required
                  placeholder="At least 6 characters"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2.5 pl-10 pr-4 text-white focus:outline-none focus:border-red-600"
                />
              </div>
            </div>

            <button type="submit" className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 rounded-lg mt-4 transition">
              Create Account
            </button>
          </form>

          <p className="mt-6 text-center text-slate-400 text-sm">
            Already have an account?{' '}
            <button onClick={() => setCurrentPage('login')} className="text-white hover:underline font-medium">
              Sign in
            </button>
          </p>
        </div>

        <p className="text-center text-xs text-slate-500">© 2026 Streamflix. All rights reserved.</p>
      </div>
    );
  }

  // --- 3. HOMEPAGE ---
  const movies = [
    { title: "Stranger Things", img: "https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?auto=format&fit=crop&q=80&w=400" },
    { title: "Cyberpunk", img: "https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&q=80&w=400" },
    { title: "Dark Knight", img: "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&q=80&w=400" },
    { title: "Interstellar", img: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=400" },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Navbar */}
      <nav className="flex items-center justify-between px-8 py-4 bg-slate-950/80 backdrop-blur-md fixed top-0 w-full z-50">
        <div className="flex items-center gap-8">
          <h1 className="text-2xl font-bold text-red-600 tracking-wider">STREAMFLIX</h1>
          <div className="hidden md:flex gap-6 text-sm text-slate-300">
            <a href="#" className="hover:text-white transition">Home</a>
            <a href="#" className="hover:text-white transition">TV Shows</a>
            <a href="#" className="hover:text-white transition">Movies</a>
            <a href="#" className="hover:text-white transition">New & Popular</a>
          </div>
        </div>
        <div className="flex items-center gap-5">
          <Search className="w-5 h-5 cursor-pointer text-slate-300 hover:text-white" />
          <Bell className="w-5 h-5 cursor-pointer text-slate-300 hover:text-white" />
          <button 
            onClick={() => setCurrentPage('login')}
            className="bg-red-600 text-white text-xs px-3 py-1.5 rounded hover:bg-red-700 transition"
          >
            Logout
          </button>
        </div>
      </nav>

      {/* Hero Banner */}
      <div className="relative h-[80vh] flex items-center px-8 bg-cover bg-center" style={{ backgroundImage: 'linear-gradient(to right, rgba(2, 6, 23, 0.9), rgba(2, 6, 23, 0.2)), url("https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?auto=format&fit=crop&q=80")' }}>
        <div className="max-w-xl space-y-4 mt-16">
          <span className="text-red-500 font-semibold tracking-widest text-sm">FEATURED SHOW</span>
          <h1 className="text-5xl font-extrabold leading-tight">Stranger Things</h1>
          <p className="text-slate-300 text-sm md:text-base leading-relaxed">
            When a young boy vanishes, a small town uncovers a mystery involving secret experiments, terrifying supernatural forces and one strange little girl.
          </p>
          <div className="flex gap-4 pt-2">
            <button className="flex items-center gap-2 bg-white text-black font-semibold px-6 py-2.5 rounded hover:bg-slate-200 transition">
              <Play className="w-5 h-5 fill-black" /> Play
            </button>
            <button className="flex items-center gap-2 bg-slate-800/80 text-white font-semibold px-6 py-2.5 rounded hover:bg-slate-700 transition backdrop-blur-md">
              <Info className="w-5 h-5" /> More Info
            </button>
          </div>
        </div>
      </div>

      {/* Movie Grid / Lists */}
      <div className="px-8 py-8 space-y-8">
        <div>
          <h2 className="text-xl font-bold mb-4">Trending Now</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {movies.map((movie, index) => (
              <div key={index} className="group relative rounded-lg overflow-hidden bg-slate-900 cursor-pointer transform hover:scale-105 transition duration-300 shadow-lg">
                <img src={movie.img} alt={movie.title} className="w-full h-48 object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent opacity-80" />
                <div className="absolute bottom-3 left-3 right-3 flex justify-between items-center">
                  <span className="font-semibold text-sm">{movie.title}</span>
                  <button className="p-1.5 bg-red-600 rounded-full hover:bg-red-700">
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
