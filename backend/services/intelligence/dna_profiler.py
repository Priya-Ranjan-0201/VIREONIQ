import numpy as np
from typing import List, Dict, Any
import json

class PsychometricDNAProfiler:
    """
    Generates and evolves the 128-Dimensional Student DNA Vector.
    """
    
    VECTOR_DIM = 128

    def generate_initial_dna(self) -> List[float]:
        """
        Creates a baseline 'New Candidate' vector.
        """
        return np.random.uniform(0.3, 0.7, self.VECTOR_DIM).tolist()

    def update_dna_from_session(self, current_dna: List[float], session_data: Dict[str, Any]) -> List[float]:
        """
        Evolves the DNA vector based on session performance.
        """
        if not current_dna:
            current_dna = self.generate_initial_dna()
            
        dna_arr = np.array(current_dna)
        
        # 1. Technical Accuracy Impact (Indices 0-20)
        tech_score = session_data.get("tech_score", 0.5)
        dna_arr[0:20] += (tech_score - 0.5) * 0.1
        
        # 2. Communication & Sentiment (Indices 21-40)
        comm_score = session_data.get("comm_score", 0.5)
        dna_arr[21:40] += (comm_score - 0.5) * 0.1
        
        # 3. Stress & Latency Resilience (Indices 41-60)
        telemetry = session_data.get("telemetry", {})
        latency_reward = 1.0 - (telemetry.get("avg_latency", 500) / 2000)
        dna_arr[41:60] += (latency_reward - 0.5) * 0.1
        
        # 4. Contextual Adaptability (Remaining indices)
        scenario_score = session_data.get("scenario_score", 0.5)
        dna_arr[61:] += (scenario_score - 0.5) * 0.05
        
        # Normalize to [0, 1]
        dna_arr = np.clip(dna_arr, 0, 1)
        
        return dna_arr.tolist()

    def identify_archetype(self, dna_vector: List[float]) -> str:
        """
        Maps high-dimensional DNA to a human-readable archetype.
        """
        dna_arr = np.array(dna_vector)
        
        # Simple projection for classification
        tech_density = np.mean(dna_arr[0:20])
        comm_density = np.mean(dna_arr[21:40])
        stress_resilience = np.mean(dna_arr[41:60])
        
        if tech_density > 0.8 and stress_resilience > 0.7:
            return "Systems Overlord (High Accuracy, High Pressure)"
        if comm_density > 0.8 and tech_density > 0.6:
            return "Engineering Evangelist (Technical Lead / Communicator)"
        if tech_density > 0.8:
            return "Quiet Architect (Deep Technical execution)"
        if stress_resilience < 0.4:
            return "Rapid Prototyper (Needs environment stability)"
            
        return "Pragmatic Engineer"
