import google.generativeai as genai
from django.conf import settings

class ScriptGeneratorService:
    def __init__(self):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            print(f"Failed to initialize Gemini AI: {str(e)}")
            self.model = None
    
    def generate_cold_call_script(self, location_name: str, category: str, machine_type: str) -> str:
        """Generate a tailored cold call script"""
        try:
            if not self.model:
                return self._get_fallback_script(location_name, category, machine_type)
            
            prompt = f"""
            Create a professional, friendly, and persuasive 1-minute cold call script for selling {machine_type} placement to {location_name}, which is a {category}.
            
            The script should:
            - Be conversational and natural (about 150-200 words)
            - Include a strong opening that gets attention
            - Highlight specific benefits relevant to this type of business
            - Address potential objections
            - Include a clear call-to-action
            - Sound professional but not overly salesy
            
            Focus on how a {machine_type} can benefit their specific type of business ({category}) and their customers.
            """
            
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
            else:
                return self._get_fallback_script(location_name, category, machine_type)
                
        except Exception as e:
            print(f"Script generation error: {str(e)}")
            return self._get_fallback_script(location_name, category, machine_type)
    
    def generate_email_template(self, location_name: str, category: str, machine_type: str) -> str:
        """Generate an email template"""
        try:
            if not self.model:
                return self._get_fallback_email(location_name, category, machine_type)
            
            prompt = f"""
            Create a professional email template for proposing {machine_type} placement at {location_name}, which is a {category}.
            
            The email should:
            - Have a compelling subject line
            - Be professional yet friendly
            - Highlight benefits specific to their business type
            - Include a clear call-to-action
            - Be concise (200-300 words)
            - End with professional signature placeholders
            
            Format it as a complete email with subject line.
            """
            
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
            else:
                return self._get_fallback_email(location_name, category, machine_type)
                
        except Exception as e:
            print(f"Email generation error: {str(e)}")
            return self._get_fallback_email(location_name, category, machine_type)
    
    def generate_in_person_script(self, location_name: str, category: str, machine_type: str) -> str:
        """Generate an in-person sales script"""
        try:
            if not self.model:
                return self._get_fallback_in_person(location_name, category, machine_type)
            
            prompt = f"""
            Create a professional in-person sales script for proposing {machine_type} placement at {location_name}, which is a {category}.
            
            The script should:
            - Include a strong introduction
            - Be conversational and adaptable
            - Address common objections
            - Highlight specific benefits for their business type
            - Include closing techniques
            - Be structured but natural (250-350 words)
            
            Format it with clear sections: Introduction, Benefits, Objection Handling, and Closing.
            """
            
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
            else:
                return self._get_fallback_in_person(location_name, category, machine_type)
                
        except Exception as e:
            print(f"In-person script generation error: {str(e)}")
            return self._get_fallback_in_person(location_name, category, machine_type)
    
    def _get_fallback_script(self, location_name: str, category: str, machine_type: str) -> str:
        """Fallback cold call script template"""
        return f"""Hi, this is [Your Name] from [Your Company]. I hope you're having a great day!

I'm reaching out because I noticed {location_name} would be a perfect location for a {machine_type}. 

These machines can provide additional revenue and convenience for your customers with no upfront cost to you. For {category} businesses like yours, we typically see great results because your customers appreciate the convenience.

The machine is fully stocked and maintained by us, and you receive a percentage of all sales. It's completely hands-off for you.

Would you have a few minutes to discuss how this could benefit your business? I'd love to show you some numbers from similar {category} locations.

What would be a good time for a quick 10-minute meeting this week?"""
    
    def _get_fallback_email(self, location_name: str, category: str, machine_type: str) -> str:
        """Fallback email template"""
        return f"""Subject: Partnership Opportunity for {location_name} - Additional Revenue Stream

Dear Manager,

I hope this email finds you well. My name is [Your Name] and I represent [Your Company], a leading {machine_type} placement service.

I've identified {location_name} as an ideal location for one of our {machine_type}s. Based on your {category} business model, I believe this could be a great additional revenue stream for you.

Here's what we offer:
- No upfront costs or installation fees
- Full maintenance and restocking service
- Revenue sharing on all sales
- Professional, modern equipment that complements your business

For {category} businesses like yours, our machines typically generate additional monthly revenue while providing convenience to your customers.

I'd love to discuss this opportunity with you in more detail. Are you available for a brief 15-minute call this week?

Best regards,
[Your Name]
[Your Phone Number]
[Your Email]
[Your Company]"""
    
    def _get_fallback_in_person(self, location_name: str, category: str, machine_type: str) -> str:
        """Fallback in-person script"""
        return f"""INTRODUCTION:
"Hi there! I'm [Your Name] from [Your Company]. I was in the area and noticed what a great {category} you have here at {location_name}. Do you have a moment to speak with the owner or manager?"

BENEFITS:
"I'd like to discuss a partnership opportunity that could provide additional revenue for your business. We place {machine_type}s in {category} businesses like yours at no cost to you.

The machine would provide convenience for your customers while generating additional income for you. We handle all maintenance, restocking, and repairs. You simply provide the space and collect your share of the profits."

OBJECTION HANDLING:
"I understand you might have concerns about space or maintenance - that's completely normal. Our machines have a small footprint and require zero work from you. We also provide full insurance coverage.

Many {category} owners are initially hesitant, but they're thrilled with the results once they see the additional revenue coming in monthly."

CLOSING:
"I have some examples of similar {category} businesses and their monthly earnings I'd love to show you. Could we schedule a quick 15-minute appointment this week to go over the details? I'm confident this could be a great fit for {location_name}."""