"""
Response Filtering System
Removes meta-commentary and extracts clean conversational content
"""
import re
from typing import List, Dict, Optional, Tuple


class ResponseFilter:
    """Filters out meta-commentary from agent responses"""
    
    def __init__(self):
        # Patterns that indicate meta-commentary to remove
        self.meta_patterns = [
            # Opening meta-commentary
            r"^Certainly!\s*Here's.*?based on.*?:",
            r"^Here's.*?structured.*?:",
            r"^Based on.*?thought process.*?:",
            r"^Let me provide.*?feedback.*?:",
            r"^I'll.*?structured.*?response.*?:",
            
            # Closing meta-commentary  
            r"This feedback.*?respectfully.*?",
            r"This.*?challenges.*?arguments.*?",
            r"This approach.*?ensures.*?",
            r"Looking forward to.*?.*?",
            r"Best regards.*?",
            r"Sincerely.*?",
            r"Talk soon.*?",
            r"Until next time.*?",
            r"I hope this.*?helpful.*?",
            
            # General meta patterns
            r"^---$",  # Horizontal separators
            r"^\*\*.*?\*\*$",  # Standalone bold headers without content
            r"^This.*?demonstrates.*?",
            r"^The.*?feedback.*?",
            r"^Moving forward.*?",
        ]
        
        # Patterns for agent identification and formal greetings
        self.agent_intro_patterns = [
            r"^\*\*Hi\s+(Barbie|Ken),?\s+this\s+is\s+(Ken|Barbie)!?\*\*",
            r"^Hi\s+(Barbie|Ken),?\s+this\s+is\s+(Ken|Barbie)!?",
            r"^Hi,?\s+I'm\s+(Barbie|Ken)!?",
            r"^\*\*(Ken|Barbie)\s+here[.!]*\*\*",
            r"^(Ken|Barbie)\s+responding:",
        ]
        
        # Keep these useful structural elements
        self.keep_patterns = [
            r"^\d+\.\s+\*\*.*?\*\*:",  # Numbered points with bold headers
            r"^-\s+",  # Bullet points
            r"^\*\s+",  # Asterisk bullets
            r"^•\s+",  # Bullet points
        ]
    
    def clean_response(self, raw_response: str, agent_name: str) -> str:
        """
        Clean agent response by removing meta-commentary
        
        Args:
            raw_response: Raw response from the agent
            agent_name: Name of the agent (for context)
            
        Returns:
            Cleaned response with only conversational content
        """
        
        # Split into lines for processing
        lines = raw_response.strip().split('\n')
        cleaned_lines = []
        
        # Process each line
        for line in lines:
            line = line.strip()
            
            # Skip empty lines temporarily
            if not line:
                continue
            
            # Check if line should be kept (structured content)
            should_keep = any(re.match(pattern, line, re.IGNORECASE) 
                            for pattern in self.keep_patterns)
            
            if should_keep:
                cleaned_lines.append(line)
                continue
            
            # Check if line is meta-commentary to remove
            is_meta = any(re.search(pattern, line, re.IGNORECASE | re.MULTILINE) 
                         for pattern in self.meta_patterns)
            
            if is_meta:
                continue
            
            # Handle agent introductions - keep only the greeting part
            intro_match = None
            for pattern in self.agent_intro_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    intro_match = match
                    break
            
            if intro_match:
                # Keep simple greeting
                other_agent = "Barbie" if agent_name.lower() == "ken" else "Ken"
                cleaned_lines.append(f"Hi {other_agent}!")
                continue
            
            # Keep everything else (actual conversational content)
            cleaned_lines.append(line)
        
        # Join lines back together
        cleaned_response = '\n'.join(cleaned_lines)
        
        # Additional cleanup
        cleaned_response = self._post_process_cleanup(cleaned_response)
        
        return cleaned_response.strip()
    
    def _post_process_cleanup(self, text: str) -> str:
        """Additional cleanup passes"""
        
        # Remove multiple consecutive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove standalone separators
        text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\*{3,}$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^={3,}$', '', text, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        text = re.sub(r' +', ' ', text)  # Multiple spaces
        text = re.sub(r'\n +', '\n', text)  # Leading spaces on lines
        
        return text
    
    def extract_conversational_content(self, raw_response: str, agent_name: str) -> Dict:
        """
        Extract and categorize different parts of the response
        
        Returns:
            Dictionary with categorized content
        """
        
        cleaned_main = self.clean_response(raw_response, agent_name)
        
        # Try to identify different sections
        sections = self._identify_sections(cleaned_main)
        
        # Extract key points if formatted as numbered list
        key_points = self._extract_key_points(cleaned_main)
        
        return {
            "main_content": cleaned_main,
            "sections": sections,
            "key_points": key_points,
            "word_count": len(cleaned_main.split()),
            "has_structure": len(key_points) > 0
        }
    
    def _identify_sections(self, text: str) -> List[Dict]:
        """Identify structured sections in the response"""
        
        sections = []
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers (numbered or bold)
            header_match = re.match(r'^(\d+)\.\s*\*\*(.*?)\*\*:', line)
            if header_match:
                # Save previous section
                if current_section:
                    current_section["content"] = '\n'.join(current_content)
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    "number": int(header_match.group(1)),
                    "title": header_match.group(2),
                    "content": ""
                }
                current_content = []
            elif current_section:
                # Add to current section content
                current_content.append(line)
            else:
                # No section structure, treat as general content
                pass
        
        # Save last section
        if current_section:
            current_section["content"] = '\n'.join(current_content)
            sections.append(current_section)
        
        return sections
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key discussion points"""
        
        key_points = []
        
        # Look for numbered points
        numbered_points = re.findall(r'^\d+\.\s+\*\*(.*?)\*\*:', text, re.MULTILINE)
        if numbered_points:
            key_points.extend(numbered_points)
        
        # Look for bullet points
        bullet_points = re.findall(r'^[-•*]\s+(.*?)$', text, re.MULTILINE)
        key_points.extend([point.strip() for point in bullet_points])
        
        return key_points
    
    def validate_response_quality(self, response: str, agent_name: str) -> Dict:
        """Validate that the response meets quality standards"""
        
        issues = []
        
        # Check for meta-commentary leakage
        for pattern in self.meta_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                issues.append(f"Contains meta-commentary: {pattern}")
        
        # Check for appropriate length
        word_count = len(response.split())
        if word_count < 20:
            issues.append("Response too short")
        elif word_count > 500:
            issues.append("Response too long")
        
        # Check for personality markers
        agent_phrases = {
            "barbie": ["imagine", "like", "beautiful", "pattern", "connects"],
            "ken": ["examine", "structure", "however", "distinguish", "mechanisms"]
        }
        
        expected_phrases = agent_phrases.get(agent_name.lower(), [])
        found_phrases = [phrase for phrase in expected_phrases 
                        if phrase in response.lower()]
        
        if len(found_phrases) < 2:
            issues.append(f"Lacks {agent_name}'s personality markers")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "word_count": word_count,
            "personality_score": len(found_phrases) / len(expected_phrases) if expected_phrases else 0
        }


class ConversationFormatter:
    """Formats cleaned responses for display"""
    
    def __init__(self):
        self.filter = ResponseFilter()
    
    def format_for_conversation(self, raw_response: str, agent_name: str, 
                               include_metadata: bool = False) -> str:
        """Format response for conversation display"""
        
        # Clean the response
        cleaned = self.filter.clean_response(raw_response, agent_name)
        
        # Add agent identifier
        formatted = f"{agent_name}: {cleaned}"
        
        # Add metadata if requested
        if include_metadata:
            validation = self.filter.validate_response_quality(cleaned, agent_name)
            metadata = f"\n[Words: {validation['word_count']}, Quality: {'✓' if validation['is_valid'] else '✗'}]"
            formatted += metadata
        
        return formatted
    
    def format_conversation_log(self, conversation_history: List[Dict], 
                               clean: bool = True) -> str:
        """Format entire conversation with optional cleaning"""
        
        formatted_lines = []
        
        for entry in conversation_history:
            speaker = entry.get("speaker", "Unknown")
            content = entry.get("content", "")
            
            if clean:
                content = self.filter.clean_response(content, speaker)
            
            formatted_lines.append(f"{speaker}: {content}")
            formatted_lines.append("")  # Add spacing
        
        return '\n'.join(formatted_lines)


def demonstrate_response_cleaning():
    """Demonstrate the response cleaning system"""
    
    # Example of problematic response (like Ken's original)
    problematic_response = """
Certainly! Here's the structured feedback based on the thought process:

---

**Hi Barbie, this is Ken!**

I appreciate your thought-provoking response, but I have some reservations
that I'd like to discuss. Your arguments are intriguing, yet I believe they
warrant a closer examination.

1. **Duality in Societal Norms**: The study by Abdelwahed (2023) highlights
how Barbie embodies both gender stereotypes and challenges societal norms.
Similarly, your discussion on simulations touches on dualities but may
oversimplify complex issues. How do you reconcile these complexities?

2. **Motivations of Simulators**: You suggest simulators might be driven by
entertainment or research. Can you provide concrete evidence from studies
supporting these motivations?

---

This feedback challenges Barbie's arguments respectfully while encouraging
her to provide more substantial evidence and considerations.
"""
    
    filter_system = ResponseFilter()
    formatter = ConversationFormatter()
    
    print("=== Response Cleaning Demo ===\n")
    
    print("BEFORE (Raw Response):")
    print("-" * 50)
    print(problematic_response)
    
    print("\nAFTER (Cleaned Response):")
    print("-" * 50)
    cleaned = filter_system.clean_response(problematic_response, "Ken")
    print(cleaned)
    
    print("\nValidation Results:")
    print("-" * 50)
    validation = filter_system.validate_response_quality(cleaned, "Ken")
    print(f"Valid: {validation['is_valid']}")
    print(f"Word Count: {validation['word_count']}")
    print(f"Issues: {validation['issues']}")
    
    print("\nFormatted for Conversation:")
    print("-" * 50)
    formatted = formatter.format_for_conversation(problematic_response, "Ken")
    print(formatted)


if __name__ == "__main__":
    demonstrate_response_cleaning()