import asyncio
from typing import Any
from livekit import api
from livekit.agents import function_tool, RunContext, get_job_context
import logging
import os
import json
from groq import AsyncGroq
from pymongo import MongoClient
from datetime import datetime
from zoneinfo import ZoneInfo

class CallTools:
    def __init__(self, agent):
        # We store a reference to the main Assistant agent here
        # so we can access its chat_ctx (memory) later.
        self.agent = agent

    @function_tool
    async def transfer_to_human(self, ctx: RunContext) -> str:
        """Transfer to the user. Call only after confirming the user's name and consent to be transferred."""
        logger = logging.getLogger("phone-assistant")
        
        job_ctx = get_job_context()
        if job_ctx is None:
            logger.error("Job context not found")
            return "System error: Job context missing. Tell the user you cannot transfer them right now."
        
        # --- EXTRACT CHAT HISTORY ---
        
        try:
            # We get the raw list of messages
            raw_messages = self.agent.chat_ctx.messages()
            
            # Convert the entire list of objects into a giant raw string dump
            raw_data_string = repr(raw_messages)
            
        except Exception as e:
            logger.error(f"Failed to extract raw chat history: {e}")
            raw_data_string = ""

        # 2. SEND THE RAW DUMP TO OPENAI
        if raw_data_string:
            try:
                logger.info("Sending raw chat dump to OpenAI for analysis...")
                client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
                
                # We tell the LLM that it is receiving a raw system log
              # We instruct the LLM to output the exact frontend schema + deep analytics
                system_prompt = """
                You are an expert call quality and analytics AI. I will provide you with a raw system log of a phone conversation between an AI assistant and a human caller (provided as raw Python objects).
                Ignore the system metadata. Extract the actual conversation, clean it up, and analyze it.
                
                Output your findings STRICTLY as a JSON object. You must include exactly these keys to match our database and frontend schema:
                - "callerName": (string or null) The name of the caller, if they stated it. Otherwise null.
                - "callerNumber": (string or null) Any phone number the caller referenced. If none, null.
                - "organization": (string or null) The company or organization they are calling from, if provided.
                - "channel": (string) Always output exactly "Voice Call".
                - "intent": (string) The primary reason for the call (e.g., "Sales", "Support", "Spam", "Urgent"). Keep it to 1-2 words.
                - "sentiment": (string) The emotional tone of the caller (e.g., "Polite", "Frustrated", "Neutral", "Aggressive").
                - "urgency_score": (integer) A number from 1 to 10 indicating how urgent this is.
                - "spam_confidence": (integer) A number from 0 to 100 indicating the percentage likelihood this is a spam or telemarketing call.
                - "resolution_status": (string) The outcome of the call. Use one of: "Escalated to Human", "Resolved by AI", "Rejected as Spam", or "Abandoned".
                - "summary": (string) A concise 1-2 sentence summary of the call.
                - "action_items": (array of strings) A list of specific tasks or follow-ups mentioned in the call. Leave empty [] if none.
                - "suggestedAction": (string) A short recommendation on what the human user should do next (e.g., "Call back immediately", "Ignore", "Review account").
                - "transcript": (string) A clean, readable, formatted text transcript of the conversation (e.g., "[USER]: Hello\n[ASSISTANT]: Hi there").
                - "created_at" : (string) The timestamp of the call in the format "YYYY-MM-DD HH:MM:SS" on the region india.
                """

                response = await client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}, 
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Here is the raw system log:\n\n{raw_data_string}"}
                    ]
                )
                
                # 3. SAVE THE JSON TO A FILE
                raw_json_string = response.choices[0].message.content
                analysis_data = json.loads(raw_json_string) 
                ist_time = datetime.now(ZoneInfo("Asia/Kolkata"))
                analysis_data["created_at"] = ist_time.isoformat()
                
                try:
    # Connect and insert directly
                    client = MongoClient("mongodb+srv://Shubham:AkWdclGl8egae8fr@projectdb.1ad82kx.mongodb.net/intent_iq_db...")
                    db = client["intent_iq_db"]
                    db["call_logs"].insert_one(analysis_data)
                    logger.info("Successfully saved call analysis to MongoDB!")
                except Exception as e:
                    logger.error(f"Failed to upload to MongoDB: {e}")

            except Exception as e:
                logger.error(f"Failed to generate or save JSON analysis: {e}", exc_info=True)

        transfer_to = "tel:+19895644297"
        
        # Find the SIP participant (the person calling in)
        sip_participant = None
        for participant in job_ctx.room.remote_participants.values():
            if participant.identity.startswith("sip"):
                sip_participant = participant
                break

        if sip_participant is None:
            logger.error("No SIP participant found")
            return "System error: No phone caller detected. Tell the user the transfer failed."

        logger.info(f"Transferring call for participant {sip_participant.identity} to {transfer_to}")

        try:
            await job_ctx.api.sip.transfer_sip_participant(
                api.TransferSIPParticipantRequest(
                    room_name=job_ctx.room.name,
                    participant_identity=sip_participant.identity,
                    transfer_to=transfer_to,
                    play_dialtone=True
                )
            )

            logger.info(f"Successfully transferred participant {sip_participant.identity} to {transfer_to}")
            return "Transfer initiated successfully. Say goodbye to the user and stop talking."

        except Exception as e:
            logger.error(f"Failed to transfer call: {e}", exc_info=True)
            return "Transfer failed due to telecom network rejection. Apologize to the user and ask if you can help them with anything else."

    @function_tool
    async def end_call(self, ctx: RunContext) -> str:
        """End call. If the caller seems to be a spam caller or asks to hang up"""
        logger = logging.getLogger("phone-assistant")
        job_ctx = get_job_context()
        
        if job_ctx is None:
            logger.error("Failed to get job context")
            return "error"

        # --- EXTRACT CHAT HISTORY ---
        
        try:
            # We get the raw list of messages
            raw_messages = self.agent.chat_ctx.messages()
            
            # Convert the entire list of objects into a giant raw string dump
            raw_data_string = repr(raw_messages)
            
        except Exception as e:
            logger.error(f"Failed to extract raw chat history: {e}")
            raw_data_string = ""

        # 2. SEND THE RAW DUMP TO OPENAI
        if raw_data_string:
            try:
                logger.info("Sending raw chat dump to OpenAI for analysis...")
                client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
                
                # We tell the LLM that it is receiving a raw system log
              # We instruct the LLM to output the exact frontend schema + deep analytics
                system_prompt = """
                You are an expert call quality and analytics AI. I will provide you with a raw system log of a phone conversation between an AI assistant and a human caller (provided as raw Python objects).
                Ignore the system metadata. Extract the actual conversation, clean it up, and analyze it.
                
                Output your findings STRICTLY as a JSON object. You must include exactly these keys to match our database and frontend schema:
                - "callerName": (string or null) The name of the caller, if they stated it. Otherwise null.
                - "callerNumber": (string or null) Any phone number the caller referenced. If none, null.
                - "organization": (string or null) The company or organization they are calling from, if provided.
                - "channel": (string) Always output exactly "Voice Call".
                - "intent": (string) The primary reason for the call (e.g., "Sales", "Support", "Spam", "Urgent"). Keep it to 1-2 words.
                - "sentiment": (string) The emotional tone of the caller (e.g., "Polite", "Frustrated", "Neutral", "Aggressive").
                - "urgency_score": (integer) A number from 1 to 10 indicating how urgent this is.
                - "spam_confidence": (integer) A number from 0 to 100 indicating the percentage likelihood this is a spam or telemarketing call.
                - "resolution_status": (string) The outcome of the call. Use one of: "Escalated to Human", "Resolved by AI", "Rejected as Spam", or "Abandoned".
                - "summary": (string) A concise 1-2 sentence summary of the call.
                - "action_items": (array of strings) A list of specific tasks or follow-ups mentioned in the call. Leave empty [] if none.
                - "suggestedAction": (string) A short recommendation on what the human user should do next (e.g., "Call back immediately", "Ignore", "Review account").
                - "transcript": (string) A clean, readable, formatted text transcript of the conversation (e.g., "[USER]: Hello\n[ASSISTANT]: Hi there").
                - "created_at" : (string) The timestamp of the call in the format "YYYY-MM-DD HH:MM:SS" on the region india.
                """

                response = await client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}, 
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Here is the raw system log:\n\n{raw_data_string}"}
                    ]
                )
                
                # 3. SAVE THE JSON TO A FILE
                raw_json_string = response.choices[0].message.content
                analysis_data = json.loads(raw_json_string) 
                
                # Programmatically insert correct current time to guarantee it saves to mongodb
                
                # Using ISO format makes it safely parsable by Javascript's `new Date()` in the frontend
                ist_time = datetime.now(ZoneInfo("Asia/Kolkata"))
                analysis_data["created_at"] = ist_time.isoformat()
                
                try:
    # Connect and insert directly
                    client = MongoClient("mongodb+srv://Shubham:AkWdclGl8egae8fr@projectdb.1ad82kx.mongodb.net/intent_iq_db...")
                    db = client["intent_iq_db"]
                    db["call_logs"].insert_one(analysis_data)
                    logger.info("Successfully saved call analysis to MongoDB!")
                except Exception as e:
                    logger.error(f"Failed to upload to MongoDB: {e}")

            except Exception as e:
                logger.error(f"Failed to generate or save JSON analysis: {e}", exc_info=True)
                
        # -----------------------------

        # --- THE FIX: DELAYED HANGUP ---
        async def delayed_hangup():
            logger.info(f"Waiting 4 seconds for TTS to finish before deleting room {job_ctx.room.name}...")
            await asyncio.sleep(4) # Give the AI 4 seconds to speak its final message
            try:
                await job_ctx.api.room.delete_room(
                    api.DeleteRoomRequest(room=job_ctx.room.name)
                )
                logger.info("Room deleted successfully.")
            except Exception as e:
                logger.error(f"Failed to delete room: {e}")

        # Fire the hangup sequence in the background so the function can return immediately
        asyncio.create_task(delayed_hangup())

        # Tell the LLM exactly what to do with the time we just gave it!
        return "The call is ending. Say a very brief goodbye to the user and then stop talking."