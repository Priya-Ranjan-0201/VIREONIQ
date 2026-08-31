import React from 'react';

export interface CompanyProfile {
  key: string;
  name: string;
  type: 'FAANG' | 'Product' | 'FinTech' | 'Service' | 'Startup';
  difficulty: 'Expert' | 'Hard' | 'Medium';
  ctc: string;
  primaryRole: string;
  jobProfiles: string[];
  roleCategory: 'sde' | 'backend' | 'frontend' | 'data_ai' | 'devops' | 'service';
  experienceLevel: string;
  location: string;
  stages: string[];
  weights: {
    DSA: number;
    Behavioral: number;
    System: number;
    CoreCS: number;
  };
  techStack: string[];
  hiringTip: string;
  lps?: number | null;
  culturePillars: string[];
  logoColor: string;
  renderLogo: () => React.ReactNode;
}

export const COMPANY_PROFILES: CompanyProfile[] = [
  // ==================== FAANG & BIG TECH ====================
  {
    key: 'google',
    name: 'Google',
    type: 'FAANG',
    difficulty: 'Expert',
    ctc: '24–58 LPA',
    primaryRole: 'Software Engineer (L3 / L4)',
    jobProfiles: [
      'Software Engineer (L3 / L4)',
      'Site Reliability Engineer (SRE)',
      'Systems Software Engineer (Infrastructure)',
      'Machine Learning Engineer'
    ],
    roleCategory: 'backend',
    experienceLevel: '0–4 Yrs (On-Campus & Lateral)',
    location: 'Bangalore, Hyderabad, Pune, Gurugram',
    stages: [
      'Online Assessment (2 Algorithmic DSA Problems)',
      'Technical Phone Screen (45 mins DSA)',
      'Onsite Coding Round 1 (Trees & Graphs)',
      'Onsite Coding Round 2 (DP & Complex Big-O)',
      'System Architecture / LLD (Distributed Scale)',
      'Googliness & Leadership Principles'
    ],
    weights: { DSA: 55, Behavioral: 15, System: 20, CoreCS: 10 },
    techStack: ['Go', 'C++', 'Java', 'Python', 'Kubernetes', 'gRPC', 'Protobuf', 'BigQuery'],
    hiringTip: 'Google emphasizes optimal time and space complexity with clean edge case handling. Always state your Big-O before writing code and think aloud.',
    lps: 5,
    culturePillars: ['Googliness', 'Bias for Action', 'Respect the User', 'Healthy Disregard for Impossible'],
    logoColor: '#4285F4',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24">
        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
      </svg>
    )
  },
  {
    key: 'amazon',
    name: 'Amazon',
    type: 'FAANG',
    difficulty: 'Hard',
    ctc: '18–48 LPA',
    primaryRole: 'Software Development Engineer (SDE-1 / SDE-2)',
    jobProfiles: [
      'Software Development Engineer I (SDE-1)',
      'Software Development Engineer II (SDE-2)',
      'Front-End Engineer (FEE)',
      'Cloud Support Engineer (AWS)'
    ],
    roleCategory: 'sde',
    experienceLevel: '0–5 Yrs (Fresher & Lateral)',
    location: 'Bangalore, Hyderabad, Chennai, Pune, Delhi NCR',
    stages: [
      'Online Assessment (2 Coding + Work Style Survey)',
      'Technical Phone Interview (DSA & LP)',
      'Onsite Round 1: Coding (Trees, Graphs & Heaps)',
      'Onsite Round 2: Object-Oriented Design (LLD)',
      'Onsite Round 3: High-Level System Architecture',
      'Onsite Round 4: Bar Raiser (Deep 16 Leadership Principles)'
    ],
    weights: { DSA: 45, Behavioral: 30, System: 15, CoreCS: 10 },
    techStack: ['Java', 'Python', 'AWS (DynamoDB, SQS, Lambda, S3)', 'C++', 'React'],
    hiringTip: 'Amazon rounds dedicate at least 15–20 minutes strictly to 16 Leadership Principles using STAR methodology. Have 5+ concrete project stories ready.',
    lps: 16,
    culturePillars: ['Customer Obsession', 'Ownership', 'Invent & Simplify', 'Are Right A Lot', 'Dive Deep'],
    logoColor: '#FF9900',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <path d="M14.5 17c-4.5 3-10 1.5-13.5-1 0 0 4.5 2.5 10 1 2-.5 3.5-1.5 3.5-1.5z" fill="#FF9900" />
        <path d="M15.5 15.5c-.3.4-.8.5-1.2.3-.4-.2-.5-.7-.3-1.1.8-1.5 2-2.2 3.5-2.2 1.5 0 2.8.7 3.5 2.2.2.4.1.9-.3 1.1-.4.2-.9.1-1.2-.3-.5-1-1.3-1.5-2-1.5-.7 0-1.5.5-2 1.5z" fill="#FF9900" />
        <path d="M7 6v6.5c0 1.4.9 2.5 2.2 2.5 1.5 0 2.8-1.2 2.8-2.7V6h-1.5v6.3c0 .8-.6 1.4-1.3 1.4-.7 0-1.2-.6-1.2-1.4V6H7z" fill="#FFFFFF" />
      </svg>
    )
  },
  {
    key: 'microsoft',
    name: 'Microsoft',
    type: 'FAANG',
    difficulty: 'Hard',
    ctc: '18–44 LPA',
    primaryRole: 'Software Engineer (L59–L62)',
    jobProfiles: [
      'Software Engineer (SDE-1 / SDE-2)',
      'Cloud Solution Architect (Azure)',
      'Data Engineer / AI Systems Developer',
      'Site Reliability Engineer'
    ],
    roleCategory: 'backend',
    experienceLevel: '0–5 Yrs',
    location: 'Hyderabad, Bangalore, Noida',
    stages: [
      'Online Assessment (3 Questions on Codility)',
      'Technical Round 1: DSA (Arrays, Strings & Trees)',
      'Technical Round 2: Low-Level & Object-Oriented Design',
      'Technical Round 3: High-Level Cloud Architecture',
      'As-Appropriate (AA) Director Round: Culture & Vision'
    ],
    weights: { DSA: 45, Behavioral: 20, System: 25, CoreCS: 10 },
    techStack: ['C#', '.NET Core', 'Azure', 'C++', 'TypeScript', 'CosmosDB', 'Kubernetes'],
    hiringTip: 'Microsoft focuses heavily on clean, modular, and readable object-oriented code with solid unit testing awareness. Practice SOLID principles.',
    lps: null,
    culturePillars: ['Growth Mindset', 'Customer Focus', 'Diversity & Inclusion', 'One Microsoft'],
    logoColor: '#00A4EF',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24">
        <rect x="2" y="2" width="9.5" height="9.5" fill="#F25022" rx="1" />
        <rect x="12.5" y="2" width="9.5" height="9.5" fill="#7FBA00" rx="1" />
        <rect x="2" y="12.5" width="9.5" height="9.5" fill="#00A4EF" rx="1" />
        <rect x="12.5" y="12.5" width="9.5" height="9.5" fill="#FFB900" rx="1" />
      </svg>
    )
  },
  {
    key: 'meta',
    name: 'Meta',
    type: 'FAANG',
    difficulty: 'Expert',
    ctc: '28–65 LPA',
    primaryRole: 'Software Engineer (E3 / E4 / E5)',
    jobProfiles: [
      'Software Engineer (Product)',
      'Software Engineer (Systems & Infra)',
      'Production Engineer (Systems & DevOps)',
      'AI / ML Infrastructure Engineer'
    ],
    roleCategory: 'sde',
    experienceLevel: '1–6 Yrs',
    location: 'Bangalore, Gurugram, Remote',
    stages: [
      'Technical Screen (2 Medium/Hard DSA in 45 min)',
      'Onsite Coding Round 1 (Fast & Bug-Free DSA)',
      'Onsite Coding Round 2 (Algorithms & Data Structures)',
      'Product Architecture / System Design (Scaling to 3B+ users)',
      'Behavioral & Impact (Past Projects & Disagreements)'
    ],
    weights: { DSA: 55, Behavioral: 15, System: 25, CoreCS: 5 },
    techStack: ['Python', 'Hack / PHP', 'C++', 'React', 'GraphQL', 'PyTorch', 'Cassandra'],
    hiringTip: 'Meta tests coding speed and precision. You are expected to write 2 optimal, working LeetCode Medium/Hard solutions in 45 minutes with zero compiler aids.',
    lps: 6,
    culturePillars: ['Move Fast', 'Focus on Long-Term Impact', 'Build Awesome Things', 'Live in Future'],
    logoColor: '#0081FB',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="#0081FB">
        <path d="M12 2.04c-5.5 0-10 4.49-10 10.02 0 5 3.66 9.15 8.44 9.9v-7H7.9v-2.9h2.54V9.85c0-2.51 1.49-3.89 3.78-3.89 1.09 0 2.23.19 2.23.19v2.47h-1.26c-1.24 0-1.63.77-1.63 1.56v1.88h2.78l-.45 2.9h-2.33v7a10 10 0 0 0 8.44-9.9c0-5.53-4.5-10.02-10-10.02z" />
      </svg>
    )
  },
  {
    key: 'apple',
    name: 'Apple',
    type: 'FAANG',
    difficulty: 'Expert',
    ctc: '25–60 LPA',
    primaryRole: 'Software Engineer (ICT2 / ICT3 / ICT4)',
    jobProfiles: [
      'Core OS & Systems Software Engineer',
      'iOS / macOS Application Developer',
      'Cloud Services & Distributed Systems Engineer',
      'Machine Learning Platform Architect'
    ],
    roleCategory: 'backend',
    experienceLevel: '1–6 Yrs',
    location: 'Bangalore, Hyderabad',
    stages: [
      'Recruiter Screen & Technical Prescreen',
      'Technical Phone Interview (Low-Level Systems & DSA)',
      'Coding Lab: Algorithmic Precision & Pointer Arithmetic',
      'Domain Architecture: Memory Hierarchy, Cache Lines & Protocols',
      'Engineering Director & Product Craftsmanship Round'
    ],
    weights: { DSA: 45, Behavioral: 15, System: 30, CoreCS: 10 },
    techStack: ['Swift', 'Objective-C', 'C', 'C++', 'Python', 'Go', 'Cassandra', 'POSIX'],
    hiringTip: 'Apple expects deep knowledge of memory management, cache lines, concurrency primitives, and extreme product craftsmanship.',
    lps: null,
    culturePillars: ['Relentless Attention to Detail', 'User Privacy', 'Hardware-Software Harmony', 'Simplicity'],
    logoColor: '#A2AAAD',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="#E2E8F0">
        <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 6.87c.66-.8 1.1-1.92.98-3.04-1 .04-2.13.66-2.79 1.43-.58.67-1.1 1.77-.96 2.87 1.12.09 2.19-.55 2.77-1.26z" />
      </svg>
    )
  },
  {
    key: 'netflix',
    name: 'Netflix',
    type: 'FAANG',
    difficulty: 'Expert',
    ctc: '35–75 LPA',
    primaryRole: 'Senior Software Engineer (L5 / L6)',
    jobProfiles: [
      'Senior Software Engineer (Distributed Systems)',
      'Streaming Algorithms & Video Delivery Engineer',
      'Data Platform & Real-Time Event Bus Engineer',
      'UI Architect / Modern Web Platforms'
    ],
    roleCategory: 'backend',
    experienceLevel: '3–8 Yrs (Top-of-Market Seniors)',
    location: 'Bangalore, Mumbai, Remote',
    stages: [
      'Technical Screen (Architecture & Deep System Discussion)',
      'Live Coding & Complex Refactoring under High Concurrency',
      'High-Scale Distributed Architecture & Chaos Engineering',
      'Culture Memo Deep-Dive with Director & VP'
    ],
    weights: { DSA: 35, Behavioral: 25, System: 35, CoreCS: 5 },
    techStack: ['Java', 'Spring Boot', 'Kafka', 'Apache Cassandra', 'GraphQL', 'AWS', 'Node.js'],
    hiringTip: 'Netflix hires predominantly senior engineers. Memorize their culture deck (Freedom & Responsibility, Context Not Control). Demonstrate high ownership.',
    lps: null,
    culturePillars: ['Freedom & Responsibility', 'Context Not Control', 'Highly Aligned Loosely Coupled', 'Stunning Colleagues'],
    logoColor: '#E50914',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="#E50914">
        <path d="M4 2h4.5l5.5 13V2h4v20h-4.5L7.5 9V22H4V2z" />
      </svg>
    )
  },
  {
    key: 'nvidia',
    name: 'Nvidia',
    type: 'FAANG',
    difficulty: 'Expert',
    ctc: '25–65 LPA',
    primaryRole: 'System Software & AI Infrastructure Engineer',
    jobProfiles: [
      'CUDA Systems Software Engineer',
      'Deep Learning Compiler & Kernel Architect',
      'GPU Distributed Training Infrastructure Engineer',
      'Autonomous Vehicles Software Engineer'
    ],
    roleCategory: 'data_ai',
    experienceLevel: '1–6 Yrs',
    location: 'Bangalore, Pune, Hyderabad',
    stages: [
      'Online Coding & Core Computing Assessment',
      'Technical Round 1: C/C++ Pointers, Memory Alignment & Data Structures',
      'Technical Round 2: Concurrency, Thread Synchronization & CUDA Kernels',
      'System Design: Distributed GPU Training Clusters & Low-Latency Fabrics',
      'Managerial & First Principles Problem Solving'
    ],
    weights: { DSA: 45, Behavioral: 15, System: 25, CoreCS: 15 },
    techStack: ['C++', 'CUDA', 'C', 'Python', 'PyTorch', 'TensorRT', 'Linux Kernel', 'RDMA'],
    hiringTip: 'Nvidia values first-principles thinking, deep understanding of CPU/GPU memory architecture, and low-level multithreading with lock-free data structures.',
    lps: null,
    culturePillars: ['First Principles Thinking', 'Speed of Light Execution', 'Craftsmanship', 'Pioneering AI'],
    logoColor: '#76B900',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="#76B900">
        <path d="M8.2 6.8c1.7-.5 3.6-.8 5.6-.8 6.4 0 10.2 4.6 10.2 10 0 5.5-4.5 9-10.8 9-5.4 0-9.8-3.4-11.2-8.5 1.5 3.7 4.9 6.2 9.1 6.2 5.3 0 9-3.7 9-8.4 0-4.6-3.8-7.9-9.3-7.9-1 0-1.8.1-2.6.4z" />
        <circle cx="8" cy="12" r="3.5" fill="#76B900" />
      </svg>
    )
  },

  // ==================== TOP PRODUCT MNCS ====================
  {
    key: 'flipkart',
    name: 'Flipkart',
    type: 'Product',
    difficulty: 'Hard',
    ctc: '16–36 LPA',
    primaryRole: 'Software Development Engineer (SDE-1 / SDE-2)',
    jobProfiles: [
      'SDE 1 (Machine Coding & Core DSA)',
      'SDE 2 (Distributed Systems & Scale)',
      'UI Engineer (React & Microfrontends)',
      'Data Platform Engineer'
    ],
    roleCategory: 'sde',
    experienceLevel: '0–4 Yrs',
    location: 'Bangalore',
    stages: [
      'Machine Coding Round (90 mins: Clean LLD with working code)',
      'DSA Problem Solving (Graphs, Trees & Sliding Window)',
      'System Architecture (E-Commerce Flash Sale Scale)',
      'Hiring Manager & Culture Alignment'
    ],
    weights: { DSA: 40, Behavioral: 15, System: 35, CoreCS: 10 },
    techStack: ['Java', 'Spring Boot', 'Kafka', 'HBase', 'Redis', 'React', 'MySQL'],
    hiringTip: 'Flipkart’s signature Machine Coding Round requires designing an extensible system with SOLID design patterns and runnable test cases within 90 minutes.',
    lps: null,
    culturePillars: ['Audacity', 'Bias for Action', 'Customer First', 'Integrity'],
    logoColor: '#2874F0',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#2874F0" />
        <path d="M6 8h12l-2 11H8L6 8z" fill="#FFE500" />
        <path d="M10 5a2 2 0 0 1 4 0v3h-4V5z" stroke="#FFE500" strokeWidth="1.5" />
      </svg>
    )
  },
  {
    key: 'uber',
    name: 'Uber',
    type: 'Product',
    difficulty: 'Expert',
    ctc: '26–60 LPA',
    primaryRole: 'Software Engineer (L3 / L4 / L5)',
    jobProfiles: [
      'Backend Engineer (Distributed Geospatial Dispatch)',
      'Frontend / Mobile Engineer (Driver & Rider Apps)',
      'Data & Machine Learning Systems Architect',
      'Infrastructure & Site Reliability Engineer'
    ],
    roleCategory: 'backend',
    experienceLevel: '1–5 Yrs',
    location: 'Bangalore, Hyderabad',
    stages: [
      'Online CodeSignal Assessment (4 Challenging Algorithmic Tasks)',
      'Coding Lab 1: DSA & Geospatial Traversal',
      'Coding Lab 2: Low-Level Concurrency & Multithreading',
      'System Design: H3/QuadTree Real-Time Dispatch & Kafka Hub',
      'Behavioral & Bar Raiser'
    ],
    weights: { DSA: 45, Behavioral: 20, System: 25, CoreCS: 10 },
    techStack: ['Go', 'Java', 'Python', 'Kafka', 'H3 Geospatial', 'Cassandra', 'MySQL'],
    hiringTip: 'Uber places heavy emphasis on concurrent programming, race conditions, distributed locking, and spatial indexing (H3, Geohash).',
    lps: null,
    culturePillars: ['Go Get It', 'Trip Obsessed', 'Build with Heart', 'Stand for Safety'],
    logoColor: '#000000',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#000000" stroke="#334155" />
        <circle cx="12" cy="12" r="5" stroke="#FFFFFF" strokeWidth="2.5" />
        <path d="M12 7v5h5" stroke="#FFFFFF" strokeWidth="2" strokeLinecap="round" />
      </svg>
    )
  },
  {
    key: 'atlassian',
    name: 'Atlassian',
    type: 'Product',
    difficulty: 'Hard',
    ctc: '22–52 LPA',
    primaryRole: 'Software Development Engineer (P3 / P4)',
    jobProfiles: [
      'Software Engineer (Jira / Confluence Cloud)',
      'Frontend Platform Architect',
      'Cloud Reliability & Platform SRE',
      'Enterprise Data Engineer'
    ],
    roleCategory: 'sde',
    experienceLevel: '1–5 Yrs',
    location: 'Bangalore, Remote (TEAM Anywhere)',
    stages: [
      'Online Assessment (Karat DSA Technical Screen)',
      'Coding Round: Clean Code, Testing & Edge Cases',
      'System Design: Real-Time Collaborative Document Sync',
      'Atlassian Values & "Don\'t #@!% the Customer" Culture Round'
    ],
    weights: { DSA: 40, Behavioral: 30, System: 25, CoreCS: 5 },
    techStack: ['Java', 'Kotlin', 'TypeScript', 'React', 'AWS', 'DynamoDB', 'Micro-frontends'],
    hiringTip: 'Atlassian weights company values as heavily as technical skill. Practice their 5 values (e.g. Open company no bullshit, Play as a team).',
    lps: 5,
    culturePillars: ['Open Company No Bullshit', 'Build with Heart & Balance', 'Don\'t #@!% the Customer', 'Play as a Team'],
    logoColor: '#0052CC',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <path d="M11.6 4.3c-.3-.5-.9-.6-1.3-.2L3.5 10c-.4.4-.4 1 0 1.4l6.8 5.9c.4.4 1 .3 1.3-.2l2.6-4.5c.3-.5.3-1.1 0-1.6l-2.6-6.7z" fill="#2684FF" />
        <path d="M12.4 19.7c.3.5.9.6 1.3.2l6.8-5.9c.4-.4.4-1 0-1.4l-6.8-5.9c-.4-.4-1-.3-1.3.2l-2.6 4.5c-.3.5-.3 1.1 0 1.6l2.6 6.7z" fill="#0052CC" />
      </svg>
    )
  },
  {
    key: 'adobe',
    name: 'Adobe',
    type: 'Product',
    difficulty: 'Hard',
    ctc: '18–44 LPA',
    primaryRole: 'Computer Scientist (MTS / SMTS)',
    jobProfiles: [
      'Member of Technical Staff (MTS)',
      'Creative Cloud Platform Engineer',
      'WebAssembly & WebGL Graphics Engineer',
      'Data & Document Cloud Architect'
    ],
    roleCategory: 'backend',
    experienceLevel: '0–5 Yrs',
    location: 'Noida, Bangalore',
    stages: [
      'HackerRank Technical Assessment (4 Questions)',
      'Technical Round 1: DSA (Trees, Graphs & Dynamic Programming)',
      'Technical Round 2: Low-Level Design & Object-Oriented Principles',
      'System Architecture: Creative Cloud Ingestion & Sync',
      'HR & Leadership Culture Fit'
    ],
    weights: { DSA: 50, Behavioral: 15, System: 25, CoreCS: 10 },
    techStack: ['C++', 'Java', 'Python', 'WebAssembly', 'WebGL', 'AWS', 'React'],
    hiringTip: 'Adobe emphasizes core computer science fundamentals (Operating Systems, Computer Graphics, Compilers) along with standard algorithmic DSA.',
    lps: null,
    culturePillars: ['Genuine', 'Exceptional', 'Innovative', 'Involved'],
    logoColor: '#FF0000',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="#FA0F00">
        <path d="M14.58 3H22v18h-4.38L14.58 3zm-5.16 0L2 21h4.38l3.04-7.46h4.63L9.42 3zM12 9.53L10.3 14.1h3.4L12 9.53z" />
      </svg>
    )
  },
  {
    key: 'salesforce',
    name: 'Salesforce',
    type: 'Product',
    difficulty: 'Hard',
    ctc: '18–45 LPA',
    primaryRole: 'Software Engineer (AMTS / MTS)',
    jobProfiles: [
      'Associate Member of Technical Staff (AMTS)',
      'Member of Technical Staff (MTS)',
      'Full Stack Cloud Developer',
      'Security & Identity Architecture Engineer'
    ],
    roleCategory: 'sde',
    experienceLevel: '0–4 Yrs',
    location: 'Hyderabad, Bangalore, Mumbai, Pune',
    stages: [
      'HackerRank Online Assessment (3 Coding Questions)',
      'Technical Round 1: Core DSA & Complex Edge Cases',
      'Technical Round 2: Object-Oriented Design & Multi-Tenant Data Isolation',
      'System Design: Scalable CRM & Distributed Messaging Pipeline',
      'Ohana Values & Managerial Round'
    ],
    weights: { DSA: 45, Behavioral: 20, System: 25, CoreCS: 10 },
    techStack: ['Java', 'Apex', 'Python', 'Kafka', 'PostgreSQL', 'Kubernetes', 'LWC (Web Components)'],
    hiringTip: 'Salesforce loves questions about multi-tenancy, database indexing, and query optimization in addition to solid LeetCode medium questions.',
    lps: null,
    culturePillars: ['Trust', 'Customer Success', 'Innovation', 'Equality', 'Sustainability'],
    logoColor: '#00A1E0',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="#00A1E0">
        <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" />
      </svg>
    )
  },

  // ==================== FINTECH & HFT ====================
  {
    key: 'stripe',
    name: 'Stripe',
    type: 'FinTech',
    difficulty: 'Expert',
    ctc: '28–65 LPA',
    primaryRole: 'Software Engineer (Infrastructure & Payments)',
    jobProfiles: [
      'Software Engineer (Payment Gateways & APIs)',
      'Infrastructure & Zero-Downtime Reliability Engineer',
      'Security, Fraud & Risk Engine Developer'
    ],
    roleCategory: 'backend',
    experienceLevel: '1–6 Yrs',
    location: 'Bangalore, Remote',
    stages: [
      'Practical Bug Squashing & Live Debugging Screen',
      'Production Coding Lab: Adding a Feature to a Real Codebase',
      'System Architecture: Idempotent Ledger & Multi-Region Payments',
      'Culture & Technical Writing Communication Interview'
    ],
    weights: { DSA: 35, Behavioral: 20, System: 35, CoreCS: 10 },
    techStack: ['Ruby', 'Java', 'Go', 'Kubernetes', 'Redis', 'Kafka', 'PostgreSQL'],
    hiringTip: 'Stripe tests practical engineering! You code in your own IDE with internet access. They look for clean code, unit tests, idempotency, and edge-case handling.',
    lps: null,
    culturePillars: ['Move with Urgency', 'Think Like an Owner', 'Rigor & Correctness', 'Developer Empathy'],
    logoColor: '#635BFF',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#635BFF" />
        <path d="M14.5 10.5c0-.8-.7-1.2-1.8-1.2-1.3 0-2.8.5-3.8 1.1V7.5c1.2-.5 2.6-.7 3.8-.7 3 0 4.8 1.5 4.8 4.1 0 3.7-5.1 3.4-5.1 5.2 0 .9.8 1.2 2 1.2 1.5 0 3.1-.6 4.2-1.3v2.8c-1.3.6-2.9.8-4.2.8-3.1 0-5.1-1.5-5.1-4.2 0-3.9 5.2-3.6 5.2-4.9z" fill="#FFFFFF" />
      </svg>
    )
  },
  {
    key: 'goldman-sachs',
    name: 'Goldman Sachs',
    type: 'FinTech',
    difficulty: 'Hard',
    ctc: '20–48 LPA',
    primaryRole: 'Software Engineer / Quantitative Strategist',
    jobProfiles: [
      'Software Engineer (Algorithmic Trading & Execution)',
      'Quantitative Strategist (Risk Engines & Financial Math)',
      'Cloud Platform & Cyber Security Engineer'
    ],
    roleCategory: 'backend',
    experienceLevel: '0–5 Yrs',
    location: 'Bangalore, Hyderabad',
    stages: [
      'HackerRank Assessment (Math, Puzzles, DP & Arrays)',
      'Technical Round 1: DSA (Dynamic Programming & Complex Recursion)',
      'Technical Round 2: Core CS (OS, DB Deadlocks, Networking & Multithreading)',
      'System Architecture: Ultra Low-Latency Order Processing',
      'Director & Culture Alignment Round'
    ],
    weights: { DSA: 45, Behavioral: 20, System: 20, CoreCS: 15 },
    techStack: ['Java', 'C++', 'Python', 'Kafka', 'Slang/SecDb', 'Hadoop', 'Linux'],
    hiringTip: 'Goldman Sachs asks probability puzzles, rigorous multithreading questions (producer-consumer, race conditions), and core OS/networking fundamentals.',
    lps: null,
    culturePillars: ['Client Service', 'Excellence', 'Integrity', 'Partnership'],
    logoColor: '#002D62',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#002D62" />
        <text x="12" y="16" fill="#73B9EE" fontSize="11" fontWeight="bold" fontFamily="sans-serif" textAnchor="middle">GS</text>
      </svg>
    )
  },
  {
    key: 'bloomberg',
    name: 'Bloomberg',
    type: 'FinTech',
    difficulty: 'Hard',
    ctc: '22–50 LPA',
    primaryRole: 'Software Engineer (Terminal & Market Data Feeds)',
    jobProfiles: [
      'Software Engineer (Real-Time Market Data)',
      'C++ Core Financial Systems Developer',
      'Data Analytics & Real-Time Visualization Architect'
    ],
    roleCategory: 'backend',
    experienceLevel: '0–5 Yrs',
    location: 'Bangalore, Pune, Remote',
    stages: [
      'Technical Phone Interview (Data Structures & Big-O)',
      'Technical Round 1: Fast Algorithmic Coding in C++/Java',
      'Technical Round 2: System Architecture & Sockets/Streaming',
      'Engineering Manager & Technical Fit Round'
    ],
    weights: { DSA: 50, Behavioral: 15, System: 25, CoreCS: 10 },
    techStack: ['C++', 'Python', 'JavaScript', 'Kafka', 'Redis', 'Linux Sockets'],
    hiringTip: 'Bloomberg requires writing production-quality C++ or Java code with clean separation of concerns and optimal memory usage for high-frequency tick data.',
    lps: null,
    culturePillars: ['Innovation', 'Collaboration', 'Customer Focus', 'Doing the Right Thing'],
    logoColor: '#1E1E1E',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#1E1E1E" stroke="#475569" />
        <text x="12" y="16" fill="#FFFFFF" fontSize="9" fontWeight="900" fontFamily="sans-serif" textAnchor="middle">BBG</text>
      </svg>
    )
  },
  {
    key: 'jpmorgan',
    name: 'JP Morgan Chase',
    type: 'FinTech',
    difficulty: 'Hard',
    ctc: '16–38 LPA',
    primaryRole: 'Software Engineer (Corporate & Investment Banking)',
    jobProfiles: [
      'Software Engineer (Payments & Transaction Ledgers)',
      'Cloud Architecture & DevOps Engineer',
      'AI / Machine Learning Fraud Prevention Engineer'
    ],
    roleCategory: 'sde',
    experienceLevel: '0–5 Yrs',
    location: 'Bangalore, Hyderabad, Mumbai',
    stages: [
      'HackerRank Coding Assessment (2 Questions)',
      'HireVue Video Behavioral Interview',
      'Technical Interview: DSA, Spring Boot & Java Collections',
      'System Architecture & Resilient Distributed Messaging',
      'Managerial Fit & Ethics Round'
    ],
    weights: { DSA: 40, Behavioral: 25, System: 20, CoreCS: 15 },
    techStack: ['Java', 'Spring Boot', 'Kafka', 'AWS', 'React', 'Oracle DB', 'Kubernetes'],
    hiringTip: 'JPMC tests solid Java collections internals (how HashMap works under the hood), concurrency, database transaction isolation levels, and ACID compliance.',
    lps: null,
    culturePillars: ['Exceptional Client Service', 'Operational Excellence', 'Integrity & Fairness', 'A Great Team'],
    logoColor: '#00539B',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#00539B" />
        <path d="M7 6h10v3H7zm0 4.5h10v3H7zm0 4.5h7v3H7z" fill="#FFFFFF" />
      </svg>
    )
  },

  // ==================== SERVICE & GLOBAL IT ====================
  {
    key: 'tcs',
    name: 'TCS (Tata Consultancy Services)',
    type: 'Service',
    difficulty: 'Medium',
    ctc: '3.6–11.5 LPA (Ninja / Digital / Prime)',
    primaryRole: 'Digital Specialist Engineer / Prime Innovator',
    jobProfiles: [
      'TCS Prime (AI & Advanced Software: 9–11.5 LPA)',
      'TCS Digital (Full Stack & Cloud: 7–8.5 LPA)',
      'TCS Ninja (Systems & Maintenance: 3.6–4.5 LPA)'
    ],
    roleCategory: 'service',
    experienceLevel: 'Freshers (On-Campus & NQT)',
    location: 'Pan-India (Bangalore, Hyderabad, Pune, Chennai, Kolkata, Delhi)',
    stages: [
      'TCS NQT Assessment (Aptitude, Verbal, Advanced Quantitative)',
      'Advanced Coding Section (2 LeetCode Medium Problems)',
      'Technical Interview (OOP, DBMS, SQL Queries & Project Viva)',
      'Managerial & HR Round'
    ],
    weights: { DSA: 40, Behavioral: 30, System: 10, CoreCS: 20 },
    techStack: ['Java', 'Python', 'C++', 'SQL', 'React', 'AWS', 'Spring Boot'],
    hiringTip: 'Score high in the TCS NQT Advanced Coding section to unlock the Digital (7.5 LPA) or Prime (11.5 LPA) interview tracks rather than standard Ninja.',
    lps: null,
    culturePillars: ['Leading Change', 'Integrity', 'Respect for Individual', 'Excellence'],
    logoColor: '#990000',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#990000" />
        <text x="12" y="16" fill="#FFFFFF" fontSize="8" fontWeight="bold" fontFamily="sans-serif" textAnchor="middle">TCS</text>
      </svg>
    )
  },
  {
    key: 'infosys',
    name: 'Infosys',
    type: 'Service',
    difficulty: 'Medium',
    ctc: '3.6–9.5 LPA (SE / DSE / Specialist)',
    primaryRole: 'Specialist Programmer / Digital Specialist',
    jobProfiles: [
      'Specialist Programmer (Power Programmer: 8–9.5 LPA)',
      'Digital Specialist Engineer (DSE: 6.5–7.5 LPA)',
      'Systems Engineer (SE: 3.6–4.2 LPA)'
    ],
    roleCategory: 'service',
    experienceLevel: 'Freshers & Lateral',
    location: 'Bangalore, Mysore, Pune, Hyderabad, Chennai, Chandigarh',
    stages: [
      'InfyTQ / HackWithInfy Coding Competition',
      'Advanced DSA Interview (Greedy, DP & Graph Traversal)',
      'Core CS Technical Round (Normalization, Deadlocks, SQL Joins)',
      'HR Behavioral Interview'
    ],
    weights: { DSA: 45, Behavioral: 25, System: 10, CoreCS: 20 },
    techStack: ['Java', 'Python', 'C#', 'SQL', 'Angular', 'Cloud Essentials'],
    hiringTip: 'Participate in HackWithInfy or excel in InfyTQ certification to bypass the 3.6 LPA SE test and land the 8.5–9.5 LPA Specialist Programmer package.',
    lps: null,
    culturePillars: ['Client Value', 'Leadership by Example', 'Integrity & Transparency', 'Fairness'],
    logoColor: '#007CC3',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#007CC3" />
        <text x="12" y="16" fill="#FFFFFF" fontSize="8" fontWeight="bold" fontFamily="sans-serif" textAnchor="middle">INFY</text>
      </svg>
    )
  },
  {
    key: 'wipro',
    name: 'Wipro',
    type: 'Service',
    difficulty: 'Medium',
    ctc: '3.5–8.5 LPA (Elite / Turbo)',
    primaryRole: 'Turbo Candidate / Project Engineer',
    jobProfiles: [
      'Wipro Turbo (High-Performance Coding: 6.5–8.5 LPA)',
      'Wipro Elite National Talent Hunt (3.5–4.2 LPA)',
      'Cloud & Cybersecurity Trainee'
    ],
    roleCategory: 'service',
    experienceLevel: 'Freshers (NLTH)',
    location: 'Bangalore, Hyderabad, Pune, Chennai, Noida',
    stages: [
      'National Talent Hunt Online Assessment',
      'Technical Interview: Object-Oriented Principles, DBMS & C/Java Code',
      'HR Round: Communication, Relocation & Willingness to Learn'
    ],
    weights: { DSA: 35, Behavioral: 35, System: 10, CoreCS: 20 },
    techStack: ['Java', 'C++', 'Python', 'SQL', 'Cloud Basics'],
    hiringTip: 'Clear both coding questions in the Elite assessment to qualify for the Turbo upgrade test, nearly doubling your starting compensation.',
    lps: null,
    culturePillars: ['Be Passionate About Clients', 'Treat Each Person with Respect', 'Unyielding Integrity'],
    logoColor: '#005880',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#005880" />
        <circle cx="9" cy="12" r="3" fill="#EA4335" />
        <circle cx="15" cy="12" r="3" fill="#FBBC05" />
      </svg>
    )
  },
  {
    key: 'accenture',
    name: 'Accenture',
    type: 'Service',
    difficulty: 'Medium',
    ctc: '4.5–12 LPA (ASE / FSE / Prime)',
    primaryRole: 'Advanced Application Engineering Associate (AAEA)',
    jobProfiles: [
      'Advanced Application Engineering Associate (AAEA: 6.5–8.5 LPA)',
      'Associate Software Engineer (ASE: 4.5–5.0 LPA)',
      'Data & AI Specialist'
    ],
    roleCategory: 'service',
    experienceLevel: 'Freshers & Lateral',
    location: 'Bangalore, Hyderabad, Pune, Mumbai, Gurugram, Chennai',
    stages: [
      'Cognitive & Technical Assessment (Aptitude, Pseudocode, Networking)',
      'Coding Assessment (2 Problem Solving Questions)',
      'Communication Voice Assessment',
      'Technical & HR Interview'
    ],
    weights: { DSA: 35, Behavioral: 35, System: 10, CoreCS: 20 },
    techStack: ['Java', 'Python', 'React', 'Cloud Services', 'SQL', 'Spring Boot'],
    hiringTip: 'Pay close attention to the Pseudocode and Technical Assessment; elimination is immediate before reaching the Coding or Interview rounds.',
    lps: null,
    culturePillars: ['Client Value Creation', 'One Global Network', 'Respect for the Individual', 'Best People'],
    logoColor: '#A100FF',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#1E1E1E" stroke="#A100FF" />
        <path d="M9 7l6 5-6 5" stroke="#A100FF" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )
  },

  // ==================== HIGH-GROWTH STARTUPS ====================
  {
    key: 'swiggy',
    name: 'Swiggy',
    type: 'Startup',
    difficulty: 'Hard',
    ctc: '18–42 LPA',
    primaryRole: 'Software Development Engineer (SDE-1 / SDE-2)',
    jobProfiles: [
      'SDE-1 (Order Lifecycle & Tracking)',
      'SDE-2 (Real-Time Logistics & Geo-Dispatch)',
      'Frontend / App Engineer'
    ],
    roleCategory: 'sde',
    experienceLevel: '1–4 Yrs',
    location: 'Bangalore',
    stages: [
      'Online Algorithmic Coding Challenge',
      'Machine Coding Round: Extensible Design with Design Patterns',
      'System Design: Hyperlocal Order Ingestion under Peak Friday Spikes',
      'Cultural Fit & Founder Values'
    ],
    weights: { DSA: 40, Behavioral: 20, System: 35, CoreCS: 5 },
    techStack: ['Go', 'Java', 'Kafka', 'Redis', 'PostgreSQL', 'AWS', 'Kubernetes'],
    hiringTip: 'Swiggy loves Machine Coding rounds in Go or Java. Focus on clear interfaces, concurrency safety, and loose coupling.',
    lps: null,
    culturePillars: ['Consumer Comes First', 'Always Be Curious', 'Stand for Integrity', 'Be Humble'],
    logoColor: '#FC8019',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#FC8019" />
        <path d="M12 4c-3.3 0-6 2.7-6 6 0 4.5 6 10 6 10s6-5.5 6-10c0-3.3-2.7-6-6-6zm0 8c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z" fill="#FFFFFF" />
      </svg>
    )
  },
  {
    key: 'zomato',
    name: 'Zomato',
    type: 'Startup',
    difficulty: 'Hard',
    ctc: '16–40 LPA',
    primaryRole: 'Product Software Engineer (SDE-1 / SDE-2)',
    jobProfiles: [
      'Full Stack Product Engineer',
      'Backend Distributed Engineer (Blinkit & Zomato)',
      'Mobile Platform Architect'
    ],
    roleCategory: 'sde',
    experienceLevel: '1–5 Yrs',
    location: 'Gurugram, Bangalore',
    stages: [
      'Technical Screen: Practical Coding & Algorithmic Foundations',
      'Deep Architecture Round: Live Code Walkthrough of Past Systems',
      'High-Concurrency System Design (Surge Pricing & Menu Sync)',
      'Culture & Founder Hustle Round'
    ],
    weights: { DSA: 35, Behavioral: 25, System: 35, CoreCS: 5 },
    techStack: ['Node.js', 'Go', 'Python', 'PHP', 'Kafka', 'Redis', 'PostgreSQL'],
    hiringTip: 'Zomato values speed of delivery and pragmatic, clean architecture. Expect in-depth questions on how you handled production outages in previous projects.',
    lps: null,
    culturePillars: ['Resilience', 'Highest Standards', 'Hustle & Speed', 'Ownership'],
    logoColor: '#CB202D',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#CB202D" />
        <text x="12" y="16" fill="#FFFFFF" fontSize="10" fontWeight="900" fontFamily="sans-serif" textAnchor="middle">Z</text>
      </svg>
    )
  },
  {
    key: 'razorpay',
    name: 'Razorpay',
    type: 'Startup',
    difficulty: 'Hard',
    ctc: '18–44 LPA',
    primaryRole: 'Software Engineer (Core Payments & Neo-Banking)',
    jobProfiles: [
      'Software Engineer (Checkout & Gateway Engine)',
      'Backend Engineer (Reconciliation & Distributed Ledgers)',
      'Security & Cryptographic Protocol Engineer'
    ],
    roleCategory: 'backend',
    experienceLevel: '1–5 Yrs',
    location: 'Bangalore',
    stages: [
      'Machine Coding / Take-Home Challenge (Extensible Architecture)',
      'Technical DSA Round (Data Structures, Graphs & Complex Queues)',
      'Distributed System Architecture (PCI-DSS & High-Availability Banking)',
      'Culture Alignment & Bar Raiser'
    ],
    weights: { DSA: 35, Behavioral: 20, System: 40, CoreCS: 5 },
    techStack: ['Go', 'PHP', 'Node.js', 'Kafka', 'Redis', 'MySQL', 'AWS'],
    hiringTip: 'Focus heavily on financial correctness, idempotency, exponential backoff with jitter for bank integrations, and webhook delivery guarantees.',
    lps: null,
    culturePillars: ['Transparency', 'Merciless Prioritization', 'Ownership', 'Customer First'],
    logoColor: '#0C2340',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#0C2340" />
        <path d="M14 4L7 14h5l-2 6 8-10h-5l1-6z" fill="#3395FF" />
      </svg>
    )
  },
  {
    key: 'zepto',
    name: 'Zepto',
    type: 'Startup',
    difficulty: 'Hard',
    ctc: '18–45 LPA',
    primaryRole: 'SDE-1 / SDE-2 (Quick Commerce Core)',
    jobProfiles: [
      'SDE-1 / SDE-2 (Dark Store & Inventory Dispatch)',
      'Frontend / Micro-App Engineer',
      'Data Engineer (Demand Forecasting & Real-Time Stock)'
    ],
    roleCategory: 'backend',
    experienceLevel: '1–4 Yrs',
    location: 'Bangalore, Mumbai',
    stages: [
      'Machine Coding / Live Coding Round (60–90 mins)',
      'Algorithmic Problem Solving (Sliding Window, Heaps & DP)',
      'System Design: Sub-10 Minute Delivery Dark Store Optimization',
      'Engineering Manager & Startup Agility Round'
    ],
    weights: { DSA: 40, Behavioral: 20, System: 35, CoreCS: 5 },
    techStack: ['Go', 'Java', 'Python', 'Kafka', 'PostgreSQL', 'Redis', 'Kubernetes'],
    hiringTip: 'Demonstrate enthusiasm for hyper-growth speed. In system design, be ready to tackle dark-store inventory race conditions when 100 users order the last item.',
    lps: null,
    culturePillars: ['Uncompromising Speed', 'Extreme Ownership', 'First Principles', 'Customer Obsessed'],
    logoColor: '#4E148C',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#4E148C" />
        <text x="12" y="16" fill="#FFC72C" fontSize="10" fontWeight="900" fontFamily="sans-serif" textAnchor="middle">Z!</text>
      </svg>
    )
  },
  {
    key: 'cred',
    name: 'CRED',
    type: 'Startup',
    difficulty: 'Hard',
    ctc: '22–50 LPA',
    primaryRole: 'Backend / Product Software Engineer',
    jobProfiles: [
      'Backend Engineer (High-Throughput Financial Rails)',
      'Frontend / Flutter Mobile Platform Architect',
      'Security & Risk Engine Engineer'
    ],
    roleCategory: 'backend',
    experienceLevel: '1–5 Yrs',
    location: 'Bangalore',
    stages: [
      'Machine Coding Round: Clean Domain-Driven Architecture',
      'DSA Problem Solving: Optimal Memory & Time Constraints',
      'System Architecture: Asynchronous Bill Fetch & Reward Engine',
      'Culture & High Taste Round with Engineering Leadership'
    ],
    weights: { DSA: 35, Behavioral: 25, System: 35, CoreCS: 5 },
    techStack: ['Go', 'Kotlin', 'Java', 'Kafka', 'PostgreSQL', 'Redis', 'AWS'],
    hiringTip: 'CRED looks for "High Taste" in software design, clean code craftsmanship, and deep architectural curiosity. Expect domain modeling questions.',
    lps: null,
    culturePillars: ['High Taste', 'Trust', 'Ownership', 'Radical Candor'],
    logoColor: '#000000',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#000000" stroke="#475569" />
        <rect x="7" y="7" width="10" height="10" rx="2" stroke="#FFFFFF" strokeWidth="2" />
        <path d="M10 10h4v4h-4z" fill="#FFFFFF" />
      </svg>
    )
  },
  {
    key: 'oracle',
    name: 'Oracle (OCI & Database)',
    type: 'Product',
    difficulty: 'Hard',
    ctc: '18–42 LPA',
    primaryRole: 'Software Developer (OCI Cloud Infrastructure)',
    jobProfiles: [
      'Software Developer (Oracle Cloud Infrastructure)',
      'Database Kernel & High-Performance Storage Engineer',
      'Autonomous Database Platform Engineer'
    ],
    roleCategory: 'backend',
    experienceLevel: '0–5 Yrs',
    location: 'Bangalore, Hyderabad, Noida',
    stages: [
      'Online Coding & Core Aptitude Assessment',
      'Technical Round 1: DSA (Arrays, Linked Lists, Trees)',
      'Technical Round 2: Core CS (OS, Multi-threading, DBMS & SQL)',
      'System Architecture: High-Availability Cloud Storage & Networking',
      'Managerial Round'
    ],
    weights: { DSA: 45, Behavioral: 15, System: 25, CoreCS: 15 },
    techStack: ['Java', 'C', 'C++', 'Go', 'Kubernetes', 'Oracle DB', 'Linux'],
    hiringTip: 'Oracle places extreme value on Operating Systems, Virtual Memory, B-Trees, and Storage Systems in addition to classic DSA.',
    lps: null,
    culturePillars: ['Integrity', 'Mutual Respect', 'Customer First', 'Communication'],
    logoColor: '#F80000',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#F80000" />
        <ellipse cx="12" cy="12" rx="6" ry="4" stroke="#FFFFFF" strokeWidth="2" />
      </svg>
    )
  },
  {
    key: 'snowflake',
    name: 'Snowflake',
    type: 'Product',
    difficulty: 'Expert',
    ctc: '30–68 LPA',
    primaryRole: 'Software Engineer (Data Cloud & Query Engine)',
    jobProfiles: [
      'Software Engineer (Query Compiler & Optimizer)',
      'Distributed Storage & Cache Infrastructure Engineer',
      'Cloud Foundation Platform Engineer'
    ],
    roleCategory: 'backend',
    experienceLevel: '1–6 Yrs',
    location: 'Pune, Bangalore, Remote',
    stages: [
      'Coding Screen (Hard LeetCode / Systems Problem)',
      'Coding Lab 1: Data Structures, Trie & Parallelism',
      'Coding Lab 2: Vectorized Execution & Concurrency',
      'System Design: Distributed Columnar Storage & Metadata Scaling',
      'Culture & Executive Bar Raiser'
    ],
    weights: { DSA: 45, Behavioral: 15, System: 30, CoreCS: 10 },
    techStack: ['C++', 'Java', 'Go', 'Python', 'FoundationDB', 'AWS', 'Azure'],
    hiringTip: 'Snowflake tests deep understanding of columnar storage, vectorized query processing, distributed consensus, and low-level C++ efficiency.',
    lps: null,
    culturePillars: ['Put Customers First', 'Integrity Always', 'Think Big', 'Get It Done'],
    logoColor: '#29B5E8',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#29B5E8" />
        <path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M18.4 5.6L5.6 18.4" stroke="#FFFFFF" strokeWidth="2" strokeLinecap="round" />
      </svg>
    )
  },
  {
    key: 'databricks',
    name: 'Databricks',
    type: 'Product',
    difficulty: 'Expert',
    ctc: '32–70 LPA',
    primaryRole: 'Software Engineer (Spark Engine & Lakehouse)',
    jobProfiles: [
      'Software Engineer (Distributed Computation)',
      'ML Platform & Generative AI Infrastructure Engineer',
      'Delta Lake & Storage Architecture Engineer'
    ],
    roleCategory: 'data_ai',
    experienceLevel: '1–6 Yrs',
    location: 'Bangalore, Remote',
    stages: [
      'Karat Prescreen (2 Algorithmic Questions in 60 mins)',
      'Technical Round 1: Hard Algorithmic Problem Solving',
      'Technical Round 2: Low-Level Concurrent Systems & Memory',
      'System Design: Petabyte-Scale Distributed Stream Processing',
      'Culture & Engineering Bar Raiser'
    ],
    weights: { DSA: 40, Behavioral: 15, System: 35, CoreCS: 10 },
    techStack: ['Scala', 'Java', 'C++', 'Python', 'Apache Spark', 'Delta Lake', 'Kubernetes'],
    hiringTip: 'Databricks interviews expect deep knowledge of distributed computing (MapReduce, Shuffle partitions, Catalyst optimizer) and concurrent data structures.',
    lps: null,
    culturePillars: ['Customer Obsession', 'Data-Driven', 'First Principles', 'Team Spirit'],
    logoColor: '#FF3621',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#1E1E1E" stroke="#FF3621" />
        <path d="M4 12l8-5 8 5-8 5-8-5z" fill="#FF3621" />
        <path d="M4 15l8 5 8-5" stroke="#FF3621" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )
  },
  {
    key: 'spotify',
    name: 'Spotify',
    type: 'Product',
    difficulty: 'Hard',
    ctc: '22–52 LPA',
    primaryRole: 'Backend / Audio Streaming Platform Engineer',
    jobProfiles: [
      'Backend Engineer (Event Bus & Audio Delivery)',
      'Web Engineer (Client Platforms & Player UI)',
      'Data & Machine Learning Recommendation Engineer'
    ],
    roleCategory: 'sde',
    experienceLevel: '1–5 Yrs',
    location: 'Bangalore, Remote',
    stages: [
      'Online Coding Challenge (Clean Code & DSA)',
      'Technical Interview: Collaborative Coding & Refactoring',
      'System Design: Distributed Audio Streaming & Real-Time Event Bus',
      'Band Values & Autonomous Squad Culture Fit'
    ],
    weights: { DSA: 40, Behavioral: 25, System: 30, CoreCS: 5 },
    techStack: ['Java', 'Python', 'GCP', 'Kafka', 'Cassandra', 'React', 'Docker'],
    hiringTip: 'Spotify places heavy emphasis on collaborative problem solving. They care as much about how you discuss trade-offs with your interviewer as the code itself.',
    lps: null,
    culturePillars: ['Innovative', 'Collaborative', 'Sincere', 'Passionate', 'Playful'],
    logoColor: '#1DB954',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="#1DB954">
        <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm4.586 14.424a.623.623 0 0 1-.857.207c-2.348-1.435-5.304-1.76-8.786-.964a.625.625 0 0 1-.281-1.218c3.808-.87 7.077-.496 9.717 1.118a.625.625 0 0 1 .207.857zm1.224-2.719a.782.782 0 0 1-1.074.258c-2.688-1.652-6.786-2.131-9.965-1.166a.78.78 0 1 1-.453-1.494c3.633-1.103 8.147-.568 11.234 1.328a.78.78 0 0 1 .258 1.074zm.105-2.835C14.692 8.95 9.375 8.775 6.297 9.71a.938.938 0 1 1-.549-1.794c3.53-1.072 9.404-.863 13.238 1.414a.938.938 0 1 1-.986 1.54z" />
      </svg>
    )
  },
  {
    key: 'airbnb',
    name: 'Airbnb',
    type: 'Product',
    difficulty: 'Hard',
    ctc: '25–58 LPA',
    primaryRole: 'Software Engineer (Search, Booking & Trust)',
    jobProfiles: [
      'Software Engineer (Search & Inventory Indexing)',
      'Frontend Platform Architect (Design Systems & Web)',
      'Trust & Safety Risk Detection Engineer'
    ],
    roleCategory: 'sde',
    experienceLevel: '1–5 Yrs',
    location: 'Bangalore, Remote',
    stages: [
      'Online Coding Prescreen (Clean Logic & Unit Tests)',
      'Production System Coding (Extending an existing codebase)',
      'System Architecture: Global Search, Availability & Reservation Locks',
      'Core Values: "Be a Host" & Belonging Interview'
    ],
    weights: { DSA: 35, Behavioral: 30, System: 30, CoreCS: 5 },
    techStack: ['Java', 'Ruby', 'Kotlin', 'React', 'GraphQL', 'MySQL', 'Kafka', 'AWS'],
    hiringTip: 'Airbnb evaluates production engineering rigor: write unit tests, handle null/undefined checks, and articulate hospitality/user empathy.',
    lps: null,
    culturePillars: ['Champion the Mission', 'Be a Host', 'Simplify', 'Every Frame Matters'],
    logoColor: '#FF5A5F',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="#FF5A5F">
        <path d="M12 2C8.5 2 6 5.5 6 9.5c0 4.5 6 12.5 6 12.5s6-8 6-12.5C18 5.5 15.5 2 12 2zm0 11.5a3.5 3.5 0 1 1 0-7 3.5 3.5 0 0 1 0 7z" />
      </svg>
    )
  },
  {
    key: 'linkedin',
    name: 'LinkedIn',
    type: 'Product',
    difficulty: 'Hard',
    ctc: '20–48 LPA',
    primaryRole: 'Software Engineer (Graph Infrastructure & Messaging)',
    jobProfiles: [
      'Software Engineer (Economic Graph & Social Feed)',
      'Distributed Systems & Kafka Pipeline Engineer',
      'UI / Frontend Web Platforms Architect'
    ],
    roleCategory: 'backend',
    experienceLevel: '1–5 Yrs',
    location: 'Bangalore',
    stages: [
      'Online HackerRank Technical Assessment (3 Questions)',
      'Technical Round 1: DSA (Graphs, BFS/DFS & Two Pointers)',
      'Technical Round 2: Concurrency & Lock-Free Data Structures',
      'System Design: Distributed Social Graph & High-Throughput Activity Feed',
      'Engineering Leadership & Culture Round'
    ],
    weights: { DSA: 45, Behavioral: 20, System: 25, CoreCS: 10 },
    techStack: ['Java', 'Kafka', 'Rest.li', 'Ember.js', 'Hadoop', 'Pinot', 'Azure'],
    hiringTip: 'LinkedIn loves graph algorithms (bipartite graphs, connected components) and asks deep questions on Kafka pub-sub architecture and partition rebalancing.',
    lps: null,
    culturePillars: ['Transformation', 'Integrity', 'Collaboration', 'Humor', 'Results'],
    logoColor: '#0A66C2',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="#0A66C2">
        <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 8.76a1.63 1.63 0 1 0 0-3.26 1.63 1.63 0 0 0 0 3.26M7.85 18.5V10.1H5.06v8.4h2.79z" />
      </svg>
    )
  },
  {
    key: 'bytedance',
    name: 'ByteDance / TikTok',
    type: 'Product',
    difficulty: 'Expert',
    ctc: '26–65 LPA',
    primaryRole: 'Software Engineer (Recommendation & Video Scale)',
    jobProfiles: [
      'Software Engineer (Video Feed & Ingestion Pipeline)',
      'Recommendation Systems Algorithm Engineer',
      'Low-Latency Microservices Developer'
    ],
    roleCategory: 'backend',
    experienceLevel: '1–5 Yrs',
    location: 'Bangalore, Singapore, Remote',
    stages: [
      'Fast LeetCode Algorithmic Prescreen (2 Medium/Hard in 50 min)',
      'Technical Round 1: Complex DP, Topological Sort & Sliding Window',
      'Technical Round 2: High-Concurrency Multithreading & Memory Safety',
      'System Design: Hyper-Scale Video Ingestion & Real-Time ML Serving',
      'ByteStyle Leadership & Velocity Round'
    ],
    weights: { DSA: 55, Behavioral: 15, System: 25, CoreCS: 5 },
    techStack: ['Go', 'Python', 'C++', 'Redis', 'Kafka', 'RocksDB', 'Kubernetes'],
    hiringTip: 'ByteDance emphasizes rapid, bug-free implementation of algorithmic problems. Practice writing code quickly with zero warnings or syntax glitches.',
    lps: null,
    culturePillars: ['Aim for the Highest', 'Be Grounded & Courageous', 'Always Day 1', 'Champion Diversity'],
    logoColor: '#00F2FE',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#111827" stroke="#00F2FE" />
        <path d="M7 6v12l4-3V9l-4-3zm6 3v9l4-3v-3l-4-3z" fill="#00F2FE" />
      </svg>
    )
  },
  {
    key: 'cisco',
    name: 'Cisco',
    type: 'Product',
    difficulty: 'Hard',
    ctc: '15–35 LPA',
    primaryRole: 'Software Engineer (Networking & Cloud Security)',
    jobProfiles: [
      'Software Engineer (Network Protocols & SDN)',
      'Cloud Security & Identity Engineer',
      'Full Stack Enterprise Applications Engineer'
    ],
    roleCategory: 'devops',
    experienceLevel: '0–5 Yrs',
    location: 'Bangalore, Pune, Chennai',
    stages: [
      'HackerRank Assessment (DSA, Linux, Sockets & Networks)',
      'Technical Round 1: DSA (Arrays, Graphs & Trees)',
      'Technical Round 2: Computer Networking (TCP/IP, Routing & Protocols)',
      'System Architecture: Distributed Mesh & Packet Processing Pipeline',
      'Managerial & HR Round'
    ],
    weights: { DSA: 40, Behavioral: 20, System: 20, CoreCS: 20 },
    techStack: ['C', 'C++', 'Python', 'Go', 'Linux', 'Docker', 'Kubernetes'],
    hiringTip: 'Brush up heavily on Computer Networks (OSI layers, TCP handshake, DNS, Subnetting, BGP) alongside standard algorithmic coding.',
    lps: null,
    culturePillars: ['Connect Everything', 'Innovate Everywhere', 'Benefit Everyone'],
    logoColor: '#1BA0D7',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#005073" />
        <path d="M4 14v3M7 11v6M10 8v9M14 8v9M17 11v6M20 14v3" stroke="#1BA0D7" strokeWidth="2" strokeLinecap="round" />
      </svg>
    )
  },
  {
    key: 'intuit',
    name: 'Intuit',
    type: 'Product',
    difficulty: 'Hard',
    ctc: '18–44 LPA',
    primaryRole: 'Software Engineer (TurboTax & QuickBooks Platforms)',
    jobProfiles: [
      'Software Development Engineer (FinTech Platform)',
      'Frontend / React Design System Architect',
      'Data & Machine Learning Fraud Detection Engineer'
    ],
    roleCategory: 'sde',
    experienceLevel: '0–4 Yrs',
    location: 'Bangalore',
    stages: [
      'Craft Demonstration / Take-Home Challenge (Presentation to Panel)',
      'Technical DSA Coding Round (Trees, Graphs & Heaps)',
      'System Architecture: Financial Ledger & Scalable Microservices',
      'Values Interview: Integrity Without Compromise & Be Bold'
    ],
    weights: { DSA: 40, Behavioral: 25, System: 25, CoreCS: 10 },
    techStack: ['Java', 'Spring Boot', 'React', 'AWS', 'Kafka', 'GraphQL', 'Kubernetes'],
    hiringTip: 'Intuit uses a unique "Craft Demonstration" where you present a real-world software project you architected and answer deep trade-off questions.',
    lps: null,
    culturePillars: ['Integrity Without Compromise', 'Customer Obsession', 'Stronger Together', 'Be Bold'],
    logoColor: '#0077C5',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#0077C5" />
        <text x="12" y="16" fill="#FFFFFF" fontSize="9" fontWeight="bold" fontFamily="sans-serif" textAnchor="middle">intuit</text>
      </svg>
    )
  },
  {
    key: 'paypal',
    name: 'PayPal',
    type: 'FinTech',
    difficulty: 'Hard',
    ctc: '18–42 LPA',
    primaryRole: 'Software Engineer (Global Payments & Risk)',
    jobProfiles: [
      'Software Development Engineer (Checkout & Wallet)',
      'Backend Distributed Ledger & Vault Engineer',
      'Risk Engine & Real-Time Fraud Prevention Architect'
    ],
    roleCategory: 'backend',
    experienceLevel: '0–5 Yrs',
    location: 'Bangalore, Chennai',
    stages: [
      'HackerRank Assessment (3 Questions on Arrays, DP & Hashing)',
      'Technical Round 1: DSA & Concurrency (Java Multithreading)',
      'Technical Round 2: Low-Level & Object-Oriented Architecture',
      'System Design: Global Settlement & High-Throughput Authorization',
      'Managerial & Cultural Alignment Round'
    ],
    weights: { DSA: 40, Behavioral: 20, System: 25, CoreCS: 15 },
    techStack: ['Java', 'Spring Boot', 'Node.js', 'Kafka', 'Oracle DB', 'GCP', 'Kubernetes'],
    hiringTip: 'PayPal tests transaction rollback mechanisms, distributed locking (Redlock / ZooKeeper), and high-throughput low-latency payment processing.',
    lps: null,
    culturePillars: ['Inclusion', 'Innovation', 'Collaboration', 'Wellness'],
    logoColor: '#003087',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#003087" />
        <text x="12" y="16" fill="#0079C1" fontSize="11" fontWeight="bold" fontFamily="sans-serif" textAnchor="middle">P</text>
      </svg>
    )
  },
  {
    key: 'cognizant',
    name: 'Cognizant',
    type: 'Service',
    difficulty: 'Medium',
    ctc: '4.0–10 LPA (GenC / Elevate / Next)',
    primaryRole: 'GenC Next / Full Stack Developer',
    jobProfiles: [
      'GenC Next (High-Scale Cloud & AI: 6.75–10 LPA)',
      'GenC Elevate (Full Stack & Advanced Coding: 4.5–5.5 LPA)',
      'GenC Programmer (3.8–4.2 LPA)'
    ],
    roleCategory: 'service',
    experienceLevel: 'Freshers (On-Campus & Off-Campus)',
    location: 'Chennai, Bangalore, Hyderabad, Pune, Kolkata, Coimbatore',
    stages: [
      'Cognizant Skill Assessment (Aptitude & Technical MCQ)',
      'Advanced Coding Challenge (2 DSA Questions)',
      'Technical Interview: SQL, OOP, Java/Python, Web Basics',
      'HR Behavioral & Communication Evaluation'
    ],
    weights: { DSA: 40, Behavioral: 30, System: 10, CoreCS: 20 },
    techStack: ['Java', 'Spring Boot', 'React', 'SQL', 'AWS', 'Python'],
    hiringTip: 'Clearing both problems in the Advanced Coding Challenge qualifies you directly for the premium GenC Next (up to 10 LPA) tier.',
    lps: null,
    culturePillars: ['Start with Passion', 'Work as One', 'Own It', 'Do the Right Thing'],
    logoColor: '#0033A0',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#0033A0" />
        <text x="12" y="16" fill="#FFFFFF" fontSize="8" fontWeight="bold" fontFamily="sans-serif" textAnchor="middle">CTS</text>
      </svg>
    )
  },
  {
    key: 'capgemini',
    name: 'Capgemini',
    type: 'Service',
    difficulty: 'Medium',
    ctc: '4.0–8.5 LPA (Analyst / Senior Analyst)',
    primaryRole: 'Senior Analyst / Software Engineer',
    jobProfiles: [
      'Senior Analyst (Advanced Coding & Cloud: 6.5–8.5 LPA)',
      'Analyst (Core Java / Full Stack: 4.0–4.5 LPA)',
      'Cloud & Infrastructure Trainee'
    ],
    roleCategory: 'service',
    experienceLevel: 'Freshers',
    location: 'Bangalore, Mumbai, Pune, Hyderabad, Chennai, Kolkata',
    stages: [
      'Pseudocode & Technical MCQ Round',
      'English Communication Assessment',
      'Game-Based Aptitude Assessment',
      'Technical & HR Interview'
    ],
    weights: { DSA: 35, Behavioral: 35, System: 10, CoreCS: 20 },
    techStack: ['Java', 'Python', 'C#', 'SQL', 'HTML/CSS/JS'],
    hiringTip: 'Practice pseudocode evaluation and game-based cognitive tests; these are unique eliminate-at-each-step filters for Capgemini hiring.',
    lps: null,
    culturePillars: ['Honesty', 'Boldness', 'Trust', 'Freedom', 'Fun'],
    logoColor: '#0070AD',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#0070AD" />
        <path d="M12 6c-3 0-5 2-5 5s2 5 5 5c2 0 3.5-.8 4.5-2.2l-1.8-1.2c-.6.8-1.5 1.4-2.7 1.4-1.7 0-3-1.3-3-3s1.3-3 3-3c1.2 0 2.1.6 2.7 1.4l1.8-1.2C15.5 6.8 14 6 12 6z" fill="#FFFFFF" />
      </svg>
    )
  },
  {
    key: 'meesho',
    name: 'Meesho',
    type: 'Startup',
    difficulty: 'Hard',
    ctc: '18–44 LPA',
    primaryRole: 'Software Development Engineer (SDE-1 / SDE-2)',
    jobProfiles: [
      'SDE-1 / SDE-2 (E-Commerce Catalog & Checkout)',
      'Data Engineer (Hyper-Scale Order Analytics)',
      'Full Stack Growth & Monetization Engineer'
    ],
    roleCategory: 'sde',
    experienceLevel: '1–4 Yrs',
    location: 'Bangalore',
    stages: [
      'Machine Coding Round: Clean OOP with Unit Tests',
      'Algorithmic DSA Round (Dynamic Programming & Trees)',
      'System Architecture: Massive 100M+ Order Scaling with Zero Downtime',
      'User First & Cultural Values Round'
    ],
    weights: { DSA: 40, Behavioral: 20, System: 35, CoreCS: 5 },
    techStack: ['Java', 'Spring Boot', 'Kafka', 'Redis', 'PostgreSQL', 'AWS', 'React'],
    hiringTip: 'Meesho moves extremely fast. In machine coding, prioritize clean, working business logic with zero compilation errors over over-engineered patterns.',
    lps: null,
    culturePillars: ['User First', 'Act Like an Owner', 'Think 10X', 'Problem Solving Mindset'],
    logoColor: '#93278F',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#93278F" />
        <text x="12" y="16" fill="#FFFFFF" fontSize="10" fontWeight="bold" fontFamily="sans-serif" textAnchor="middle">m</text>
      </svg>
    )
  },
  {
    key: 'postman',
    name: 'Postman',
    type: 'Startup',
    difficulty: 'Hard',
    ctc: '20–46 LPA',
    primaryRole: 'Software Engineer (API Platform & Cloud)',
    jobProfiles: [
      'Software Engineer (API Runtime & Collaboration)',
      'Electron / Desktop Performance Architect',
      'Cloud Infrastructure & High-Availability SRE'
    ],
    roleCategory: 'sde',
    experienceLevel: '1–5 Yrs',
    location: 'Bangalore, Remote',
    stages: [
      'Take-Home Practical Coding Challenge (API Design)',
      'Code Review & Pair Programming Interview',
      'System Architecture: Global API Network & Collaborative Workspaces',
      'Culture & Developer Empathy Round'
    ],
    weights: { DSA: 35, Behavioral: 25, System: 35, CoreCS: 5 },
    techStack: ['Node.js', 'TypeScript', 'Electron', 'React', 'MySQL', 'Redis', 'AWS'],
    hiringTip: 'Postman focuses heavily on API design best practices (REST, GraphQL, gRPC, WebSocket), HTTP protocols, and developer experience empathy.',
    lps: null,
    culturePillars: ['Developer Empathy', 'Create with Passion', 'Own the Outcome', 'Learn & Grow'],
    logoColor: '#FF6C37',
    renderLogo: () => (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
        <rect width="24" height="24" rx="6" fill="#FF6C37" />
        <circle cx="12" cy="12" r="5" stroke="#FFFFFF" strokeWidth="2" />
        <path d="M12 9l3 3-3 3" stroke="#FFFFFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )
  }
];

