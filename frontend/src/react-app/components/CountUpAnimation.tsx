import { motion, useSpring, useTransform } from 'framer-motion';
import { useEffect } from 'react';

interface CountUpAnimationProps {
  value: number;
  duration?: number;
  className?: string;
  suffix?: string;
  prefix?: string;
}

export default function CountUpAnimation({ 
  value, 
  duration = 2,
  className = '',
  suffix = '',
  prefix = ''
}: CountUpAnimationProps) {
  const spring = useSpring(0, { 
    bounce: 0,
    duration: duration * 1000 
  });
  
  const display = useTransform(spring, (latest) => 
    prefix + Math.floor(latest).toLocaleString() + suffix
  );

  useEffect(() => {
    spring.set(value);
  }, [spring, value]);

  return (
    <motion.span className={className}>
      {display}
    </motion.span>
  );
}
