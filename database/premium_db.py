import motor.motor_asyncio
from info import DATABASE_URI, DATABASE_NAME
import datetime
from datetime import datetime, timedelta

class PremiumDB:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URI)
        self.db = self.client[DATABASE_NAME]
        self.premium_col = self.db["premium_users"]
        self.usage_col = self.db["daily_usage"]
        self.referral_col = self.db["referrals"]
    
    async def add_premium_user(self, user_id, days, plan_name, payment_method="Referral"):
        """Add premium user"""
        expiry_date = datetime.now() + timedelta(days=days)
        
        premium_data = {
            "user_id": user_id,
            "plan_name": plan_name,
            "days": days,
            "expiry_date": expiry_date,
            "payment_method": payment_method,
            "purchase_date": datetime.now(),
            "is_active": True
        }
        
        await self.premium_col.update_one(
            {"user_id": user_id},
            {"$set": premium_data},
            upsert=True
        )
        return True
    
    async def remove_premium(self, user_id):
        """Remove premium from user"""
        await self.premium_col.delete_one({"user_id": user_id})
        return True
    
    async def is_premium(self, user_id):
        """Check if user is premium"""
        user = await self.premium_col.find_one({"user_id": user_id})
        
        if not user:
            return False
        
        # Check if premium expired
        expiry_date = user.get("expiry_date")
        if isinstance(expiry_date, str):
            expiry_date = datetime.fromisoformat(expiry_date)
        
        if datetime.now() > expiry_date:
            # Premium expired, remove
            await self.remove_premium(user_id)
            return False
        
        return True
    
    async def get_premium_info(self, user_id):
        """Get premium user info"""
        user = await self.premium_col.find_one({"user_id": user_id})
        return user
    
    async def get_all_premium_users(self):
        """Get all premium users"""
        users = await self.premium_col.find({"is_active": True}).to_list(length=None)
        return users
    
    async def track_daily_usage(self, user_id):
        """Track daily downloads for free users"""
        today = datetime.now().date()
        
        # Check if user is premium
        if await self.is_premium(user_id):
            return True  # Premium users have no limits
        
        # Check daily usage for free user
        usage = await self.usage_col.find_one({
            "user_id": user_id,
            "date": str(today)
        })
        
        if not usage:
            # First download today
            await self.usage_col.insert_one({
                "user_id": user_id,
                "date": str(today),
                "downloads": 1
            })
            return True
        else:
            # Check if reached daily limit
            from info import DAILY_FREE_LIMIT
            if usage["downloads"] >= DAILY_FREE_LIMIT:
                return False
            else:
                # Increment download count
                await self.usage_col.update_one(
                    {"user_id": user_id, "date": str(today)},
                    {"$inc": {"downloads": 1}}
                )
                return True
    
    async def get_today_downloads(self, user_id):
        """Get today's download count"""
        today = datetime.now().date()
        usage = await self.usage_col.find_one({
            "user_id": user_id,
            "date": str(today)
        })
        return usage["downloads"] if usage else 0
    
    async def reset_daily_usage(self):
        """Reset daily usage (run via cron job)"""
        yesterday = datetime.now() - timedelta(days=1)
        await self.usage_col.delete_many({"date": str(yesterday.date())})
        return True
    
    # Referral system
    async def add_referral(self, referrer_id, referred_id):
        """Add referral"""
        referral_data = {
            "referrer_id": referrer_id,
            "referred_id": referred_id,
            "date": datetime.now(),
            "points_credited": False
        }
        
        await self.referral_col.insert_one(referral_data)
        return True
    
    async def get_referral_count(self, user_id):
        """Get total referrals by user"""
        count = await self.referral_col.count_documents({
            "referrer_id": user_id,
            "points_credited": False
        })
        return count
    
    async def get_user_points(self, user_id):
        """Get user referral points"""
        referrals = await self.get_referral_count(user_id)
        from info import REFERRAL_POINTS_PER_REF
        return referrals * REFERRAL_POINTS_PER_REF
    
    async def redeem_points(self, user_id, points_to_redeem):
        """Redeem points for premium"""
        user_points = await self.get_user_points(user_id)
        
        if user_points < points_to_redeem:
            return False, "Insufficient points"
        
        # Mark referrals as credited
        await self.referral_col.update_many(
            {"referrer_id": user_id, "points_credited": False},
            {"$set": {"points_credited": True}},
            limit=points_to_redeem
        )
        
        # Add premium days
        from info import POINTS_TO_DAYS_RATIO
        days = points_to_redeem * POINTS_TO_DAYS_RATIO
        
        await self.add_premium_user(
            user_id, 
            days, 
            f"{points_to_redeem} Points Redemption", 
            "Referral Points"
        )
        
        return True, f"Success! {days} days premium added."

# Create instance
premium_db = PremiumDB()