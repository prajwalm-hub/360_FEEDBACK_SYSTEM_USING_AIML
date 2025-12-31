import { motion } from 'framer-motion';
import { Sparkles, Zap, TrendingUp, Award, Target, Activity } from 'lucide-react';
import PageTransition from '@/react-app/components/PageTransition';
import AnimatedCard from '@/react-app/components/AnimatedCard';
import StaggerContainer, { staggerItemVariants } from '@/react-app/components/StaggerContainer';
import AnimatedButton from '@/react-app/components/AnimatedButton';
import ScrollReveal from '@/react-app/components/ScrollReveal';
import CountUpAnimation from '@/react-app/components/CountUpAnimation';
import ParallaxSection from '@/react-app/components/ParallaxSection';
import { NewsCardSkeleton } from '@/react-app/components/SkeletonLoader';

export default function AnimationShowcase() {
  const stats = [
    { icon: TrendingUp, value: 15234, label: 'Total Articles', color: 'from-blue-500 to-cyan-500' },
    { icon: Award, value: 98, label: 'Accuracy Rate', suffix: '%', color: 'from-purple-500 to-pink-500' },
    { icon: Target, value: 45, label: 'Active Sources', color: 'from-orange-500 to-red-500' },
    { icon: Activity, value: 1234, label: 'Daily Updates', color: 'from-green-500 to-emerald-500' },
  ];

  const features = [
    { 
      title: 'Page Transitions', 
      description: 'Smooth fade and slide transitions between pages',
      icon: '🎬',
      demo: 'Automatic when navigating'
    },
    { 
      title: 'Stagger Animations', 
      description: 'Cards appear sequentially with delayed timing',
      icon: '📊',
      demo: 'See cards below'
    },
    { 
      title: 'Micro Interactions', 
      description: 'Hover and tap effects on interactive elements',
      icon: '✨',
      demo: 'Hover over any card'
    },
    { 
      title: 'Scroll Reveals', 
      description: 'Elements animate into view as you scroll',
      icon: '👁️',
      demo: 'Scroll down to see'
    },
    { 
      title: 'Count Up Numbers', 
      description: 'Statistics animate from 0 to target value',
      icon: '🔢',
      demo: 'Stats cards above'
    },
    { 
      title: 'Parallax Effects', 
      description: 'Background elements move at different speeds',
      icon: '🌊',
      demo: 'Scroll to experience'
    },
    { 
      title: 'Skeleton Loaders', 
      description: 'Professional shimmer loading states',
      icon: '⏳',
      demo: 'Loading card below'
    },
    { 
      title: 'Morphing Cards', 
      description: 'Cards transform shape and scale on hover',
      icon: '🎨',
      demo: 'Hover feature cards'
    },
  ];

  return (
    <PageTransition className="space-y-12 pb-12">
      {/* Hero Section with Gradient Animation */}
      <div className="relative overflow-hidden bg-gradient-to-br from-purple-600 via-pink-600 to-red-600 rounded-3xl p-12 text-white">
        <motion.div
          className="absolute inset-0 opacity-30"
          animate={{
            backgroundPosition: ['0% 0%', '100% 100%'],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            repeatType: 'reverse',
          }}
          style={{
            backgroundImage: 'radial-gradient(circle, white 1px, transparent 1px)',
            backgroundSize: '50px 50px',
          }}
        />
        
        <div className="relative z-10 text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', duration: 0.8 }}
            className="inline-block mb-4"
          >
            <Sparkles className="w-16 h-16" />
          </motion.div>
          
          <motion.h1
            className="text-5xl font-bold mb-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            Next-Level Animations
          </motion.h1>
          
          <motion.p
            className="text-xl opacity-90 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            Experience smooth, professional animations powered by Framer Motion
          </motion.p>
          
          <motion.div
            className="flex justify-center space-x-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <AnimatedButton icon={<Zap />}>
              Get Started
            </AnimatedButton>
            <AnimatedButton variant="outline" className="bg-white/10 border-white text-white hover:bg-white/20">
              Learn More
            </AnimatedButton>
          </motion.div>
        </div>
      </div>

      {/* Stats with Count Up Animation */}
      <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={index}
            variants={staggerItemVariants}
            className="morph-card"
          >
            <AnimatedCard delay={index * 0.1}>
              <div className={`bg-gradient-to-br ${stat.color} rounded-2xl p-6 text-white shadow-xl`}>
                <stat.icon className="w-8 h-8 mb-4 opacity-80" />
                <div className="text-4xl font-bold mb-2">
                  <CountUpAnimation 
                    value={stat.value} 
                    suffix={stat.suffix || ''} 
                  />
                </div>
                <div className="text-sm opacity-90">{stat.label}</div>
              </div>
            </AnimatedCard>
          </motion.div>
        ))}
      </StaggerContainer>

      {/* Feature Grid with Scroll Reveal */}
      <div className="space-y-6">
        <ScrollReveal>
          <h2 className="text-3xl font-bold text-center bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            Animation Features
          </h2>
        </ScrollReveal>

        <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <ScrollReveal key={index} delay={index * 0.1} direction={index % 2 === 0 ? 'left' : 'right'}>
              <motion.div
                variants={staggerItemVariants}
                whileHover={{ scale: 1.05, rotate: 2 }}
                className="morph-card bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-2xl transition-shadow duration-300"
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-lg font-bold mb-2 text-gray-900 dark:text-white">{feature.title}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{feature.description}</p>
                <div className="text-xs text-purple-600 dark:text-purple-400 font-semibold">
                  💡 {feature.demo}
                </div>
              </motion.div>
            </ScrollReveal>
          ))}
        </StaggerContainer>
      </div>

      {/* Parallax Section */}
      <ParallaxSection speed={0.3}>
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl p-12 text-white text-center">
          <h2 className="text-4xl font-bold mb-4">Parallax Scrolling</h2>
          <p className="text-xl opacity-90">This section moves at a different speed as you scroll</p>
        </div>
      </ParallaxSection>

      {/* Skeleton Loader Demo */}
      <ScrollReveal>
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-white">
            Loading State Animation
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <NewsCardSkeleton />
            <NewsCardSkeleton />
          </div>
        </div>
      </ScrollReveal>

      {/* Interactive Cards with Magnetic Effect */}
      <ScrollReveal direction="up">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((item) => (
            <motion.div
              key={item}
              whileHover={{ 
                scale: 1.05,
                boxShadow: '0 20px 50px rgba(147, 51, 234, 0.3)'
              }}
              whileTap={{ scale: 0.95 }}
              className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl p-8 text-white cursor-pointer animate-magnetic-pulse"
            >
              <div className="text-6xl font-bold mb-4">{item}</div>
              <h3 className="text-xl font-semibold mb-2">Interactive Card</h3>
              <p className="opacity-90">Hover for magnetic pulse effect</p>
            </motion.div>
          ))}
        </div>
      </ScrollReveal>

      {/* Gradient Shifting Text */}
      <div className="text-center py-12">
        <h2 className="text-6xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 bg-clip-text text-transparent animate-gradient-shift mb-4">
          Animated Gradients
        </h2>
        <p className="text-gray-600 dark:text-gray-400">Watch the gradient shift and flow</p>
      </div>
    </PageTransition>
  );
}
