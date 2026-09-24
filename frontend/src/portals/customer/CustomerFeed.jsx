import React, { useState } from "react";
import {
  Bookmark,
  Share2,
  Heart,
  ArrowRight,
  Sparkles,
  Search,
  Leaf,
  CheckCircle2,
  MoreVertical,
} from "lucide-react";
import ServiceDetailsModal from "../../components/ServiceDetailsModal";

export default function CustomerFeed({ onBackToDashboard }) {
  const [liked, setLiked] = useState(false);
  const [saved, setSaved] = useState(false);
  const [likeCount, setLikeCount] = useState(124);
  const [activeCategory, setActiveCategory] = useState("For you");
  const [searchQuery, setSearchQuery] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  const categories = ["For you", "Research", "Discoveries", "Projects", "Fun facts"];

  const handleLike = () => {
    if (liked) {
      setLiked(false);
      setLikeCount(likeCount - 1);
    } else {
      setLiked(true);
      setLikeCount(likeCount + 1);
    }
  };

  return (
    <div className="min-h-screen bg-[#fbf9f4] text-[#1f2824] pb-24">
      {/* App Top Bar */}
      <div className="sticky top-0 z-20 bg-[#143628] text-[#fbf9f4] px-4 py-3 shadow-md">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-[#fbf9f4] text-[#143628] flex items-center justify-center font-bold">
              <Leaf size={18} />
            </div>
            <div>
              <span className="font-serif-brand font-bold text-sm text-[#fbf9f4] block leading-none">PRASAD</span>
              <span className="text-[8px] text-[#c4a462] tracking-widest uppercase block mt-0.5">
                FARM CARE 360°
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs text-[#d0dfc5] font-semibold hidden sm:inline">Good morning, Pavan</span>
            <button
              onClick={onBackToDashboard}
              className="btn-gold py-1 px-3 text-xs font-bold"
            >
              My Dashboard 🏡
            </button>
          </div>
        </div>
      </div>

      {/* Dual Tab Header Bar */}
      <div className="bg-[#143628] text-[#fbf9f4] pb-6 px-4">
        <div className="max-w-3xl mx-auto space-y-4">
          <div className="flex items-center gap-2 bg-[#1b4d39] p-1.5 rounded-2xl border border-[#2a6b4e] mt-2">
            <button className="flex-1 py-2 rounded-xl font-bold text-xs sm:text-sm bg-[#143628] text-[#fbf9f4] shadow-sm">
              📖 Feed
            </button>
            <button
              onClick={onBackToDashboard}
              className="flex-1 py-2 rounded-xl font-bold text-xs sm:text-sm text-[#d0dfc5] hover:text-[#fbf9f4]"
            >
              🏡 My Dashboard
            </button>
          </div>

          {/* Search Bar (Image 07) */}
          <div className="relative">
            <Search className="absolute left-3.5 top-3 w-4 h-4 text-[#8c9790]" />
            <input
              type="text"
              placeholder="Search stories and updates"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#1b4d39] border border-[#2a6b4e] rounded-xl pl-10 pr-4 py-2.5 text-xs text-[#fbf9f4] placeholder-[#8c9790] focus:outline-none focus:border-[#c4a462]"
            />
          </div>

          {/* Category Filter Pills (Image 07) */}
          <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pt-1">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-4 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
                  activeCategory === cat
                    ? "bg-[#fbf9f4] text-[#143628]"
                    : "bg-[#1b4d39] text-[#d0dfc5] hover:bg-[#2a6b4e]"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Feed Content Container */}
      <div className="max-w-3xl mx-auto px-4 py-6 space-y-8">
        {/* Featured Hero Story Card (Image 07) */}
        <div className="relative rounded-3xl overflow-hidden shadow-sm border border-[#e8e2d5] aspect-[16/9] group">
          <img
            src="https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=1200&q=80"
            alt="Fresh ideas"
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent"></div>
          <div className="absolute top-4 left-4 bg-[#c4a462] text-[#143628] text-[10px] font-bold px-3 py-1 rounded-full uppercase">
            FROM FARMCARE
          </div>
          <div className="absolute bottom-4 left-4 right-4 text-[#fbf9f4] space-y-2">
            <h2 className="font-serif-brand font-bold text-2xl sm:text-3xl leading-tight">
              Fresh ideas for greener spaces
            </h2>
            <p className="text-xs text-[#d0dfc5]">Discover what we are exploring this season.</p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="btn-gold py-1.5 px-4 text-xs font-bold text-[#143628] inline-flex items-center gap-1"
            >
              Read story ↗
            </button>
          </div>
        </div>

        {/* Section: More stories for you (Image 07) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-serif-brand text-xl font-bold text-[#143628]">More stories for you</h2>
            <span className="text-xs font-semibold text-[#143628] cursor-pointer hover:underline">
              See all &gt;
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div
              onClick={() => setIsModalOpen(true)}
              className="bg-[#f5f2ea] border border-[#e8e2d5] rounded-2xl p-4 space-y-3 cursor-pointer hover:border-[#143628] transition-all group"
            >
              <div className="h-36 rounded-xl overflow-hidden relative">
                <img
                  src="https://images.unsplash.com/photo-1592417817098-8f3d6eb12755?auto=format&fit=crop&w=600&q=80"
                  alt="Inside our next garden concept"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <span className="absolute top-2 left-2 bg-[#143628]/90 text-[#fbf9f4] text-[9px] font-bold px-2 py-0.5 rounded uppercase">
                  PROJECT PREVIEW
                </span>
              </div>
              <div>
                <h3 className="font-serif-brand font-bold text-base text-[#143628]">
                  Inside our next garden concept
                </h3>
                <p className="text-xs text-[#6b7770]">Smarter spaces. Healthier harvests.</p>
              </div>
              <div className="flex justify-end">
                <div className="w-7 h-7 rounded-full bg-[#e2ebe4] text-[#143628] flex items-center justify-center">
                  <ArrowRight size={14} />
                </div>
              </div>
            </div>

            <div
              onClick={() => setIsModalOpen(true)}
              className="bg-[#f5f2ea] border border-[#e8e2d5] rounded-2xl p-4 space-y-3 cursor-pointer hover:border-[#143628] transition-all group"
            >
              <div className="h-36 rounded-xl overflow-hidden relative">
                <img
                  src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=600&q=80"
                  alt="Life beneath soil"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <span className="absolute top-2 left-2 bg-[#c4a462] text-[#143628] text-[9px] font-bold px-2 py-0.5 rounded uppercase">
                  FUN FACT
                </span>
              </div>
              <div>
                <h3 className="font-serif-brand font-bold text-base text-[#143628]">
                  Meet the life beneath your soil
                </h3>
                <p className="text-xs text-[#6b7770]">A hidden world that helps us grow.</p>
              </div>
              <div className="flex justify-end">
                <div className="w-7 h-7 rounded-full bg-[#e2ebe4] text-[#143628] flex items-center justify-center">
                  <ArrowRight size={14} />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Section: Article Feed Item (Image 07) */}
        <div className="bg-[#f5f2ea] border border-[#e8e2d5] rounded-3xl p-5 space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-[#143628] text-[#c4a462] flex items-center justify-center font-bold text-xs">
                FC
              </div>
              <div>
                <span className="font-bold text-xs text-[#143628] block">
                  FarmCare Editorial • Research notes
                </span>
                <span className="text-[10px] text-[#6b7770]">2 days ago</span>
              </div>
            </div>
            <button className="text-[#6b7770] hover:text-[#143628]">
              <MoreVertical size={16} />
            </button>
          </div>

          <h3 className="font-serif-brand font-bold text-xl text-[#143628]">
            A closer look at smarter watering
          </h3>

          <div className="h-52 rounded-2xl overflow-hidden border border-[#e8e2d5]">
            <img
              src="https://images.unsplash.com/photo-1592417817098-8f3d6eb12755?auto=format&fit=crop&w=1000&q=80"
              alt="Smarter watering"
              className="w-full h-full object-cover"
            />
          </div>

          <p className="text-xs text-[#4a5850]">
            A practical introduction to drip irrigation planning, moisture sensors, and conservation techniques for your plots.
          </p>

          <div className="flex items-center justify-between pt-2 border-t border-[#e8e2d5] text-xs">
            <button
              onClick={() => setIsModalOpen(true)}
              className="font-bold text-[#143628] hover:underline"
            >
              Read more ↗
            </button>

            <div className="flex items-center gap-4 text-[#6b7770]">
              <button
                onClick={handleLike}
                className={`flex items-center gap-1 hover:text-[#143628] ${liked ? "text-red-600 font-bold" : ""}`}
              >
                <Heart size={16} className={liked ? "fill-current" : ""} />
                <span>{likeCount}</span>
              </button>
              <button
                onClick={() => setSaved(!saved)}
                className={`hover:text-[#143628] ${saved ? "text-[#143628]" : ""}`}
              >
                <Bookmark size={16} className={saved ? "fill-current" : ""} />
              </button>
              <button className="hover:text-[#143628]">
                <Share2 size={16} />
              </button>
            </div>
          </div>
        </div>

        <p className="text-center text-[11px] text-[#6b7770] italic">
          Illustrative content. For a greener, brighter tomorrow.
        </p>
      </div>

      <ServiceDetailsModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        service={{
          title: "Smarter Watering & Garden Planning",
          subtitle: "Explore our automated drip irrigation and soil testing options.",
          image: "https://images.unsplash.com/photo-1592417817098-8f3d6eb12755?auto=format&fit=crop&w=1000&q=80"
        }}
      />
    </div>
  );
}
