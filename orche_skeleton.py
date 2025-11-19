# ================================================================
# PCU Components (Services)
# ================================================================
import re

class SensingLayer:
    def ingest(self, raw_data):
        """Receive raw streaming data."""
        return {"sensed": raw_data}


class PersonicleEngine:
    def __init__(self):
        """Initialize PersonicleEngine with state tracking."""
        self.previous_glucose = None  # Track previous glucose value for spike detection
    
    def extract(self, sensed):
        """Convert sensed data into processed data and events. Performs noise filtering."""
        # Extract the actual sensed data
        sensed_data = sensed.get('sensed', sensed) if isinstance(sensed, dict) else sensed
        
        if not isinstance(sensed_data, dict):
            # For non-dict data, return as-is with generic event
            return {"processed_data": sensed_data, "events": f"evt({sensed_data})", "noise": False}
        
        processed_data = {}
        events = []
        is_noise = False
        
        # Check if heart rate data is present
        if 'hr' in sensed_data:
            hr = sensed_data['hr']
            
            # Noise filtering: if HR is clearly out of range, mark as noise
            if hr < 30 or hr >= 180:
                is_noise = True
                return {"noise": True, "events": "noise", "processed_data": None}
            
            # Process valid HR data
            processed_data['hr'] = hr
            
            # Detect events within normal range
            if 70 <= hr < 85:
                # Normal range, on the lower side - warning
                events.append("warning")
            elif 85 <= hr < 100:
                # Normal range, on the higher side - likely exercising
                events.append("exercising")
            # HR in [30, 70) or [100, 180) will be judged by StateEstimationModule
        
        # Check if glucose data is present
        if 'glucose' in sensed_data:
            glucose = sensed_data['glucose']
            
            # Noise filtering: if glucose is clearly out of physiological range, mark as noise
            if glucose < 20 or glucose > 500:
                is_noise = True
                return {"noise": True, "events": "noise", "processed_data": None}
            
            # Process valid glucose data
            processed_data['glucose'] = glucose
            
            # Track glucose for spike detection (but don't judge here - that's StateEstimationModule's job)
            # Update previous glucose value
            self.previous_glucose = glucose
        
        # Handle other data types
        for key, value in sensed_data.items():
            if key not in ['hr', 'glucose']:
                processed_data[key] = value
        
        # Combine events or return single event
        if len(events) == 0:
            event = "normal"
        elif len(events) == 1:
            event = events[0]
        else:
            event = "; ".join(events)
        
        return {"processed_data": processed_data, "events": event, "noise": False}


class StateEstimationModule:
    def __init__(self):
        """Initialize StateEstimationModule with state tracking."""
        self.previous_glucose = None  # Track previous glucose for spike detection
    
    def update(self, personicle_output):
        """Update physiological/behavioral/emotional state based on PersonicleEngine output."""
        # Check if it's noise
        if personicle_output.get('noise', False):
            return {"state": "noise"}
        
        # Extract processed data and events
        processed_data = personicle_output.get('processed_data', {})
        events = personicle_output.get('events', '')
        
        if not isinstance(processed_data, dict):
            return {"state": f"state({events})"}
        
        states = []
        
        # Judge heart rate states
        if 'hr' in processed_data:
            hr = processed_data['hr']
            if hr < 70:
                states.append(f"heart rate too low, heart rate={hr}")
            elif hr >= 100:
                states.append(f"heart rate too high, heart rate={hr}")
            # Normal range [70, 100) is handled by PersonicleEngine events (exercising/warning)
        
        # Judge glucose states
        if 'glucose' in processed_data:
            glucose = processed_data['glucose']
            
            # Track glucose for spike detection
            if self.previous_glucose is not None:
                glucose_change = glucose - self.previous_glucose
                # Detect glucose spike (eating event)
                if glucose_change > 20:
                    states.append(f"glucose spike, glucose={glucose} mg/dL, spike={glucose_change:.1f} mg/dL")
                elif glucose < 70:
                    states.append(f"glucose too low, glucose={glucose} mg/dL")
                elif glucose > 180:
                    states.append(f"glucose too high, glucose={glucose} mg/dL")
            else:
                # First glucose reading
                if glucose < 70:
                    states.append(f"glucose too low, glucose={glucose} mg/dL")
                elif glucose > 180:
                    states.append(f"glucose too high, glucose={glucose} mg/dL")
                elif glucose > 140:
                    states.append(f"glucose spike, glucose={glucose} mg/dL, spike=initial elevated reading")
            
            # Update previous glucose value
            self.previous_glucose = glucose
        
        # Combine states with events from PersonicleEngine
        if len(states) == 0:
            state_str = events if events else "normal"
        else:
            state_parts = [events] + states if events and events != "normal" else states
            state_str = "; ".join(state_parts)
        
        return {"state": state_str, "processed_data": processed_data}


class KnowledgeBase:
    def retrieve(self, state):
        """Provide domain knowledge relevant to the state."""
        # Extract clean data for readable output
        state_data = state.get('state', state) if isinstance(state, dict) else str(state)
        
        # Generate domain-specific guidance based on state
        knowledge_guidance = ""
        
        if "heart rate too low" in state_data:
            knowledge_guidance = "Knowledge: Low heart rate may indicate rest, sleep, or potential bradycardia. Normal resting HR is 60-100 bpm for adults."
        elif "heart rate too high" in state_data:
            knowledge_guidance = "Knowledge: Elevated heart rate can result from exercise, stress, caffeine, or medical conditions. Target HR during moderate activity is 50-70% of max (220-age)."
        elif "glucose spike" in state_data:
            knowledge_guidance = "Knowledge: Post-meal glucose typically peaks 1-2 hours after eating. Healthy post-meal glucose is <140 mg/dL. Large spikes may indicate high-carb meals or insulin resistance."
        elif "glucose too low" in state_data:
            knowledge_guidance = "Knowledge: Hypoglycemia (<70 mg/dL) requires immediate attention. Quick-acting carbs (15g) can help raise glucose. If severe, seek medical help."
        elif "glucose too high" in state_data:
            knowledge_guidance = "Knowledge: Hyperglycemia (>180 mg/dL) may indicate diabetes or poor glucose control. Monitor diet, exercise, and consider consulting healthcare provider."
        else:
            knowledge_guidance = f"Knowledge: General health monitoring for state: {state_data}"
        
        return {"knowledge": knowledge_guidance, "state": state_data}


class ContextualInferenceEngine:
    def infer(self, state, knowledge):
        """Interpret user's situation/intent."""
        # Extract clean values to avoid nested string escaping
        state_val = state.get('state', '') if isinstance(state, dict) else str(state)
        knowledge_val = knowledge.get('knowledge', '') if isinstance(knowledge, dict) else str(knowledge)
        return {"context": f"context(state={state_val}, knowledge={knowledge_val})", "knowledge_guidance": knowledge_val}


class GuidanceGenerator:
    def generate(self, context):
        """Generate nudges, insights, explanations."""
        # Extract context data and knowledge guidance
        context_data = context.get('context', context) if isinstance(context, dict) else str(context)
        knowledge_guidance = context.get('knowledge_guidance', '') if isinstance(context, dict) else ''
        
        # Parse context to extract meaningful information and generate personalized guidance
        # Check for glucose spike events first (highest priority)
        if "glucose spike" in context_data:
            glucose_match = re.search(r'glucose=([\d.]+)', context_data)
            spike_match = re.search(r'spike=([\d.]+)', context_data)  # Just capture the number
            glucose_value = glucose_match.group(1) if glucose_match else "unknown"
            spike_value = spike_match.group(1) if spike_match else "unknown"
            if "initial" in context_data.lower():
                base_msg = f"Insight: Glucose spike detected (eating event). Your glucose is {glucose_value} mg/dL (elevated reading)."
            else:
                base_msg = f"Insight: Glucose spike detected (eating event). Your glucose is {glucose_value} mg/dL (spike: +{spike_value} mg/dL)."
            guidance_msg = f"{base_msg} {knowledge_guidance} Consider tracking your meal timing and composition."
        
        # Check for PersonicleEngine events (exercising, warning)
        elif "exercising" in context_data:
            base_msg = "Insight: Your heart rate pattern suggests you may be exercising."
            guidance_msg = f"{base_msg} {knowledge_guidance if knowledge_guidance else 'Keep up the good work!'}"
        elif "warning" in context_data:
            base_msg = "Notice: Your heart rate is in the lower normal range."
            guidance_msg = f"{base_msg} {knowledge_guidance if knowledge_guidance else 'Monitor your condition.'}"
        
        # Check for heart rate events
        elif "heart rate too low" in context_data:
            # Extract heart rate value
            hr_match = re.search(r'heart rate=(\d+)', context_data)
            hr_value = hr_match.group(1) if hr_match else "unknown"
            base_msg = f"Recommendation: Your heart rate ({hr_value} bpm) is below normal."
            guidance_msg = f"{base_msg} {knowledge_guidance} Consider resting or consulting a healthcare provider if this persists."
        elif "heart rate too high" in context_data:
            # Extract heart rate value
            hr_match = re.search(r'heart rate=(\d+)', context_data)
            hr_value = hr_match.group(1) if hr_match else "unknown"
            base_msg = f"Recommendation: Your heart rate ({hr_value} bpm) is elevated."
            guidance_msg = f"{base_msg} {knowledge_guidance} Consider taking a break, deep breathing, or consulting a healthcare provider if this persists."
        
        # Check for glucose events
        elif "glucose too low" in context_data:
            glucose_match = re.search(r'glucose=([\d.]+)', context_data)
            glucose_value = glucose_match.group(1) if glucose_match else "unknown"
            base_msg = f"Alert: Your glucose ({glucose_value} mg/dL) is below normal."
            guidance_msg = f"{base_msg} {knowledge_guidance} Consider having a snack or consulting a healthcare provider if this persists."
        elif "glucose too high" in context_data:
            glucose_match = re.search(r'glucose=([\d.]+)', context_data)
            glucose_value = glucose_match.group(1) if glucose_match else "unknown"
            base_msg = f"Alert: Your glucose ({glucose_value} mg/dL) is elevated."
            guidance_msg = f"{base_msg} {knowledge_guidance} Consider monitoring your diet and consulting a healthcare provider if this persists."
        else:
            if knowledge_guidance:
                guidance_msg = f"{knowledge_guidance} Additional context: {context_data}"
            else:
                guidance_msg = f"Guidance based on: {context_data}"
        
        return {"guidance": guidance_msg}


class InterfaceLayer:
    def deliver(self, message):
        """Deliver guidance to user or caregiver."""
        # Format message in a more readable way
        print(f"[Interface] Recommendation:")
        print(f"  {message}")

# ================================================================
# Orchestrator (Central Brain)
# ================================================================

class Orchestrator:
    def __init__(self, sensing, personicle, state_estimator,
                 knowledge, context_engine, guidance, interface):

        self.sensing = sensing
        self.personicle = personicle
        self.state_estimator = state_estimator
        self.knowledge = knowledge
        self.context_engine = context_engine
        self.guidance = guidance
        self.interface = interface

    def handle_new_data(self, raw_data):
        """Entry point for streaming data."""

        # 1. Ingest data
        sensed = self.sensing.ingest(raw_data)
        print(f"[SensingLayer] Output: {sensed}")

        # 2. Extract events and process data (noise filtering)
        personicle_output = self.personicle.extract(sensed)
        
        # Display PersonicleEngine output
        if personicle_output.get('noise', False):
            print(f"[PersonicleEngine] Output: noise (data filtered)")
        else:
            processed_data = personicle_output.get('processed_data', {})
            events_str = personicle_output.get('events', '')
            print(f"[PersonicleEngine] Output: processed_data={processed_data}, events={events_str}")

        # Now orchestrator decides what to do based on PersonicleEngine output
        next_action = self.decide_next_step(personicle_output)
        print(f"[Orchestrator] Decision: {next_action}")

        # 3. Route logic
        if next_action == "update_state":
            state = self.state_estimator.update(personicle_output)
            state_str = state.get('state', '') if isinstance(state, dict) else str(state)
            print(f"[StateEstimationModule] Output: {state_str}")
            
            knowledge = self.knowledge.retrieve(state)
            knowledge_str = knowledge.get('knowledge', '') if isinstance(knowledge, dict) else str(knowledge)
            print(f"[KnowledgeBase] Output: {knowledge_str}")
            
            context = self.context_engine.infer(state, knowledge)
            context_str = context.get('context', '') if isinstance(context, dict) else str(context)
            print(f"[ContextualInferenceEngine] Output: {context_str}")
            
            guidance = self.guidance.generate(context)
            guidance_str = guidance.get('guidance', '') if isinstance(guidance, dict) else str(guidance)
            print(f"[GuidanceGenerator] Output: {guidance_str}")
            print()  # Add spacing before interface delivery
            
            self.interface.deliver(guidance_str)

        elif next_action == "ignore":
            print("[Orchestrator] Data logged but not providing recommendation at this time.")

        elif next_action == "log_only":
            print("[Orchestrator] Data logged but not providing recommendation at this time.")

        else:
            print("[Orchestrator] Undefined event type:", next_action)

    def decide_next_step(self, personicle_output):
        """
        Decide PCU workflow dynamically based on PersonicleEngine output.
        """
        # Check for noise first
        if personicle_output.get('noise', False):
            return "ignore"
        
        # Extract events and processed data
        events = personicle_output.get('events', '')
        processed_data = personicle_output.get('processed_data', {})
        
        # If there's data that needs state estimation, trigger update_state
        # This includes HR or glucose data that needs judgment
        if isinstance(processed_data, dict):
            if 'hr' in processed_data or 'glucose' in processed_data:
                return "update_state"
        
        # For other events (exercising, warning, normal), log only
        if events in ["exercising", "warning", "normal"]:
            return "log_only"
        
        # Default to log_only
        return "log_only"


# ================================================================
# TEST
# ================================================================
if __name__ == "__main__":

    # Instantiate services
    sensing = SensingLayer()
    personicle = PersonicleEngine()
    state_estimator = StateEstimationModule()
    knowledge = KnowledgeBase()
    context_engine = ContextualInferenceEngine()
    guidance = GuidanceGenerator()
    interface = InterfaceLayer()

    # Create orchestrator
    orchestrator = Orchestrator(
        sensing, personicle, state_estimator,
        knowledge, context_engine, guidance, interface
    )

    # Simulated streaming data
    data_stream = [
        {"hr": 82},              # Normal range [70, 100)
        {"hr": 50},              # Too low [30, 70)
        {"glucose": 95},         # Normal glucose (baseline)
        {"glucose": 120},        # Normal glucose
        {"glucose": 155},        # Glucose spike (eating detected: >140 and +35 from previous)
        {"glucose": 145},        # Still elevated but normalizing
        {"hr": 140},             # Too high [100, 180)
        {"hr": 25},              # Noise (< 30)
        {"glucose": 65},         # Glucose too low
        {"glucose": 200},        # Glucose too high
        {"hr": 200},             # Noise (>= 180)
        {"idle": True},          # Non-HR/glucose data
    ]

    print("\n" + "=" * 60)
    print("Running PCU Orchestrator Test")
    print("=" * 60 + "\n")
    
    # Print the data stream that will be processed
    print("Data Stream to Process:")
    print("-" * 60)
    for i, packet in enumerate(data_stream, 1):
        print(f"  [{i}] {packet}")
    print("-" * 60)
    print("\nPress any key to start PCU")
    input()

    for i, packet in enumerate(data_stream, 1):
        print(f"\n[{i}/{len(data_stream)}] Processing new data: {packet}")
        print("-" * 60)
        orchestrator.handle_new_data(packet)
        print("-" * 60)
        
        # Wait for keypress before processing next packet (except for the last one)
        if i < len(data_stream):
            print(f"\nPress any key to process next new data ({i+1}/{len(data_stream)})...")
            input()
