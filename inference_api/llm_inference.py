import os
import logging
from dotenv import  load_dotenv
from openai import OpenAI

from scrapping.populate_vectordb import PopulateVectorDB

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PopulateVectorDB = PopulateVectorDB()

class LLMInference:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.model_name1 = os.getenv("MODEL_NAME1","google/gemini-2.0-flash-thinking-exp:free")
        self.model_name2 = os.getenv("MODEL_NAME2","deepseek/deepseek-r1:free")
        self.model_name3 = os.getenv("MODEL_NAME3","meta-llama/llama-3.3-70b-instruct:free")
        self.model = os.getenv("MODEL_NAME2","mistralai/mistral-small-3.1-24b-instruct:free")
        self.client = OpenAI(   
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv('OPENROUTER_API_KEY',"")
        )

    def create_prompt(self, context: str, query: str, chat_history: str = None) -> str:
        """
        Create a prompt for the LLM. This method can be customized to generate different prompts.
        
        Parameters
        ----------
        context : str
            The context or background information for the LLM.
        query : str
            The specific question or request to the LLM.
        chat_history : str, optional  
            Previous chat history to provide context for the LLM.
        Returns
        -------
        str
            The generated prompt.
        """
        try:
            logger.info("Creating system prompt...")
            system_prompt = f"""
            You are a helpful assistant. Answer the user query best possible to address the user's needs.
            You are given a context and a query.
            Context: {context}. 
            History : {chat_history}.
            
            Query: {query}.

            """
            return system_prompt
        except Exception as e:
            logger.error(f"Error in creating prompt: {e}")
            return None
    def llm_inference(self,system_prompt : str = "You are a helpful assistant."):
        """
        LLM Inference code to generate text based on the provided system prompt.

        Parameters
        -----------
        system_prompt : str
            The system prompt to guide the LLM's response.

        Returns
        -------
        str
            The generated text from the LLM.
        """
        try:
            logger.info(f"LLM Inference started with system prompt")
            completion = self.client.chat.completions.create(
            temperature=0.7,
            extra_body={
                "models":[self.model_name1, self.model_name2]
            },
            model=self.model_name2,
            messages=[
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": system_prompt
                    },
                    
                ]
                }
            ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM Inference failed: {e}")
            return None
   
    def get_response(self,  query: str, chat_history: str = None) -> str:
        """
        Get the response from the LLM based on the context and query.

        Parameters
        ----------
        query : str 
            The specific question or request to the LLM.
        chat_history : str, optional    
            Previous chat history to provide context for the LLM.
        
        Returns
        -------
        str
            The response from the LLM.
        """ 
        try:
            logger.info("Generating response from LLM...")
            context_dict = PopulateVectorDB.get_retrieved_data(namespace="zain", query=query)
            context = ""
            if context_dict is None:
                logger.error("No context found for the given query.")
               
            for data in context_dict:
                context = context+"  "+data['text']+"\n"

            system_prompt = self.create_prompt(context, query, chat_history)
            if system_prompt:
                response = self.llm_inference(system_prompt)
                return response
            else:
                logger.error("Failed to create system prompt.")

                return "Apologies, I am unable to assist you  due to technical reasons visit the website."
        except Exception as e:
            logger.error(f"Error in getting LLM response: {e}")
            return None

    