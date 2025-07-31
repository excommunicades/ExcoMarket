import os
import re
import redis
import requests
from telegram import Update, ReplyKeyboardMarkup
from dotenv import load_dotenv
from telegram.ext import ContextTypes, CommandHandler

load_dotenv()

redis_host = os.getenv("REDIS_HOST", "redis")
backend_host = os.getenv("BACKEND_HOST", "web")

redis_client = redis.Redis(host=redis_host, port=6379, decode_responses=True)

def set_user_state(user_id: int, state: str | None):
    """Set or clear the user's current conversation state in Redis."""
    key = f"user:{user_id}:state"
    if state:
        redis_client.set(key, state)
    else:
        redis_client.delete(key)

def get_user_state(user_id: int) -> str | None:
    """Retrieve the user's current conversation state from Redis."""
    return redis_client.get(f"user:{user_id}:state")

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    """Handle /start command and greet the user."""

    keyboard = [
        ["🔐 Log in", "📝 Register", "💉 Health Check"],
        ["🔍 Search", "🛠 Populate Products"],
        ["👤 Profile", "💰 Reward", "🧹 Clear Wallet"],
        ["➕ Subscribe", "➖ Unsubscribe", "👥 List Users"],
        ["📃 List Products", "🔍 Product Detail", "💸 Purchase Product"],
        ["➕ Create Product", "✏️ Update Product", "🗑 Delete Product"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    welcome_text = (
        "👋 Welcome! Use the buttons below.\n\n"
        "🔐 Log in: Log in user`\n"
        "📝 Register: Register user`\n"
        "🔍 Search: search AI assistant, write query to him\n"
        "💉 Health Check: check backend DB health\n"
        "🛠 Populate Products: create 50 random products\n"
        "👤 Profile: get your profile with products and wallet\n"
        "💰 Reward: add 500 coins to your wallet\n"
        "🧹 Clear Wallet: reset your wallet balance to zero\n"
        "➕ Create Product: create new product\n"
        "📃 List Products: return list of all products\n"
        "🔍 Product Detail: get detailed information about a specific product\n"
        "✏️ Update Product: update your specific product\n"
        "🗑 Delete Product: delete your specific product\n"
        "💸 Purchase Product: buy a product\n"
        "➕ Subscribe: subscribe to a seller (you will be prompted for seller ID)\n"
        "➖ Unsubscribe: unsubscribe from a seller (you will be prompted for seller ID)\n"
        "👥 List Users: get list of all users\n"
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    """Process incoming text messages based on the user's current state."""

    text = update.message.text.strip()
    user_id = update.message.from_user.id
    state = get_user_state(user_id)

    backend_user_id = redis_client.get(f"user:telegram:{user_id}:backend_id")
    jwt_token = redis_client.get(f"user:{backend_user_id}:jwt") if backend_user_id else None
    headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else {}

    if text == "🔐 Log in":
        set_user_state(user_id, "login")
        await update.message.reply_text("🔐 Please enter your email and password separated by comma:")
        return

    if text == "📝 Register":
        set_user_state(user_id, "register")
        await update.message.reply_text(
            "📝 Please enter nickname, email, password and confirm_password separated by comma:\n"
            "`nickname,email,password,confirm_password`"
        )
        return

    if text == "🔍 Search":
        set_user_state(user_id, "search")
        await update.message.reply_text("🤖 Hello! I am your search assistant based on artificial intelligence. Enter your search query:")
        return

    if text == "💉 Health Check":

        try:
            response = requests.get(f"http://{backend_host}:5000/manage/health")
            if response.status_code == 200:
                data = response.json()
                await update.message.reply_text(f"✅ Health Check OK:\n{data}")
            else:
                await update.message.reply_text(f"❌ Health Check failed: {response.text}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error during Health Check:\n{e}")
        return

    if text == "🛠 Populate Products":

        backend_user_id = redis_client.get(f"user:telegram:{user_id}:backend_id")
        if not backend_user_id:
            await update.message.reply_text("❌ You need to log in first to populate products.")
            return

        jwt_token = redis_client.get(f"user:{backend_user_id}:jwt")
        if not jwt_token:
            await update.message.reply_text("❌ JWT token not found. Please log in again.")
            return

        try:
            response = requests.post(
                f"http://{backend_host}:5000/manage/populate/products",
                headers={"Authorization": f"Bearer {jwt_token}"}
            )
            if response.status_code == 201:
                data = response.json()
                await update.message.reply_text(f"✅ {data.get('msg')}")
            else:
                await update.message.reply_text(f"❌ Failed to populate products: {response.text}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error during populating products:\n{e}")
        return

    if text in ["👤 Profile", "💰 Reward", "🧹 Clear Wallet"]:

        backend_user_id = redis_client.get(f"user:telegram:{user_id}:backend_id")
        if not backend_user_id:
            await update.message.reply_text("❌ You need to log in first.")
            return

        jwt_token = redis_client.get(f"user:{backend_user_id}:jwt")
        if not jwt_token:
            await update.message.reply_text("❌ JWT token not found. Please log in again.")
            return

        if text == "👤 Profile":

            try:
                response = requests.get(f"http://{backend_host}:5000/profile/", headers=headers)
                if response.status_code == 200:
                    profile = response.json()
                    msg_lines = [
                        f"👤 Profile: {profile.get('nickname', 'N/A')}",
                        f"📧 Email: {profile.get('email', 'N/A')}",
                        f"💰 Wallet balance: {profile.get('wallet', 0)}",
                        f"🛍 Products:"
                    ]
                    products = profile.get('active_products') or profile.get('products') or []
                    if products:
                        msg_lines.append(f"-     ID     |     NAME    |     PRICE     ")
                        for p in products:
                            msg_lines.append(f"- {p.get('id', 'N/F')} | {p.get('name', 'Unnamed')} | Price: {p.get('price', 'N/A')} UAH")
                    else:
                        msg_lines.append("No products found.")

                    msg_lines.append("\n📣 Subscriptions:")
                    subscriptions = profile.get('subscriptions', [])
                    if subscriptions:
                        for s in subscriptions:
                            msg_lines.append(f"- {s.get('nickname', 'Unknown')} ({s.get('email', 'No email')})")
                    else:
                        msg_lines.append("No subscriptions found.")

                    await update.message.reply_text("\n".join(msg_lines))
                else:
                    await update.message.reply_text(f"❌ Failed to get profile: {response.text}")
            except Exception as e:
                await update.message.reply_text(f"⚠️ Error getting profile:\n{e}")
            return

        if text == "💰 Reward":

            try:
                response = requests.post(f"http://{backend_host}:5000/wallet/reward", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    await update.message.reply_text(f"💰 {data.get('message')}\nNew balance: {data.get('new_balance')}")
                else:
                    await update.message.reply_text(f"❌ Failed to reward user: {response.text}")
            except Exception as e:
                await update.message.reply_text(f"⚠️ Error rewarding user:\n{e}")
            return

        if text == "🧹 Clear Wallet":

            try:
                response = requests.post(f"http://{backend_host}:5000/wallet/clear", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    await update.message.reply_text(f"🧹 {data.get('message')}\nNew balance: {data.get('new_balance')}")
                else:
                    await update.message.reply_text(f"❌ Failed to clear wallet: {response.text}")
            except Exception as e:
                await update.message.reply_text(f"⚠️ Error clearing wallet:\n{e}")
            return

    if text == "➕ Subscribe":

        if not jwt_token:
            await update.message.reply_text("❌ Please log in first.")
            return
        set_user_state(user_id, "subscribe")
        await update.message.reply_text("➕ Please enter the seller ID to subscribe:")
        return

    if text == "➖ Unsubscribe":

        if not jwt_token:
            await update.message.reply_text("❌ Please log in first.")
            return
        set_user_state(user_id, "unsubscribe")
        await update.message.reply_text("➖ Please enter the seller ID to unsubscribe:")
        return

    if text == "👥 List Users":

        if not jwt_token:
            await update.message.reply_text("❌ Please log in first.")
            return
        await update.message.reply_text("👥 Fetching all users...")
        try:
            response = requests.get(f"http://{backend_host}:5000/manage/users", headers=headers)
            if response.status_code == 200:
                users = response.json().get("users", [])
                if not users:
                    await update.message.reply_text("No users found.")
                else:
                    lines = [f"👥 Users ({len(users)}):"]
                    for u in users:
                        lines.append(f"- #{u.get('id')} {u.get('nickname')}")
                    await update.message.reply_text("\n".join(lines))
            else:
                await update.message.reply_text(f"❌ Failed to get users: {response.text}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error fetching users:\n{e}")
        return

    if text == "➕ Create Product":

        if not jwt_token:
            await update.message.reply_text("❌ Please log in first.")
            return
        set_user_state(user_id, "create_product")
        await update.message.reply_text(
            "➕ Creating product.\n"
            "Please enter product details in format:\n"
            "name, price, description\n"
            "(Use semicolon `,` as separator)"
        )
        return

    if text == "📃 List Products":

        try:
            response = requests.get(f"http://{backend_host}:5000/products", headers=headers)
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", [])
                if not products:
                    await update.message.reply_text("No available products found.")
                    return
                lines = [f"📃 Products list ({len(products)}):"]
                for p in products:
                    lines.append(f"- #{p.get('id')} {p.get('name')} | Price: {p.get('price')}")
                await update.message.reply_text("\n".join(lines))
            else:
                await update.message.reply_text(f"❌ Failed to get products: {response.text}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error fetching products:\n{e}")
        return

    if text == "🔍 Product Detail":

        set_user_state(user_id, "get_product_detail")
        await update.message.reply_text("🔍 Please enter product ID to get details:")
        return

    if text == "✏️ Update Product":

        if not jwt_token:
            await update.message.reply_text("❌ Please log in first.")
            return
        set_user_state(user_id, "update_product_ask_id")
        await update.message.reply_text(
            "✏️ Update product.\n"
            "Please enter product ID to update:"
        )
        return

    if text == "🗑 Delete Product":

        if not jwt_token:
            await update.message.reply_text("❌ Please log in first.")
            return
        set_user_state(user_id, "delete_product")
        await update.message.reply_text("🗑 Please enter product ID to delete:")
        return

    if text == "💸 Purchase Product":

        if not jwt_token:
            await update.message.reply_text("❌ Please log in first.")
            return
        set_user_state(user_id, "purchase_product")
        await update.message.reply_text("💸 Please enter product ID to purchase:")
        return

    # -------------STATES-------------

    if state == "login":

        try:
            nickname_or_email, password = [part.strip() for part in text.split(',', 1)]
        except ValueError:
            await update.message.reply_text("❌ Invalid format. Use: `email password`")
            return

        response = requests.post(f"http://{backend_host}:5000/auth/login", json={
            "nickname_or_email": nickname_or_email,
            "password": password,
        })

        if response.status_code == 200:
            data = response.json()
            user_id_backend = data.get("user", {}).get("id")
            jwt_token = data.get("access_token") or data.get("token")  # подставь правильное имя поля

            if user_id_backend and jwt_token:
                redis_client.set(f"user:telegram:{user_id}:backend_id", user_id_backend)
                redis_client.set(f"user:{user_id_backend}:chat_id", update.message.chat_id)
                redis_client.set(f"user:{user_id_backend}:jwt", jwt_token)
                set_user_state(user_id, None)
                await update.message.reply_text("✅ Successfully authorized!")
            else:
                await update.message.reply_text("❌ Login response missing user id or token.")
        else:
            await update.message.reply_text(f"❌ Authorization failed: {response.text}")
        return

    if state == "register":

        parts = [part.strip() for part in text.split(',')]
        if len(parts) != 4:
            await update.message.reply_text("❌ Invalid format. Use: `nickname email password confirm_password`")
            return

        nickname, email, password, confirm_password = parts
        if password != confirm_password:
            await update.message.reply_text("❌ Passwords do not match.")
            return

        response = requests.post(f"http://{backend_host}:5000/auth/register", json={
            "nickname": nickname,
            "email": email,
            "password": password,
            "confirm_password": confirm_password,
        })

        if response.status_code == 201:
            set_user_state(user_id, None)
            await update.message.reply_text("✅ Registration successful! You can now log in.")
        else:
            await update.message.reply_text(f"❌ Registration failed: {response.text}")
        return

    if state == "search":

        query = text
        await update.message.reply_text(f"🔎 Searching products for: \"{query}\"... ⏳")

        try:
            response = requests.post(f"http://{backend_host}:5000/ai_search/search", json={"query": query})
            if response.status_code == 200:
                result_text = response.json().get("result", "").strip()
                if result_text == "No matching products.":
                    await update.message.reply_text("❌ No matching products found.")
                    return

                products = re.findall(
                    r'Product #(\d+): Name: (.*?), Price: ([\d.]+) UAH, Description: (.+?)(?=(?:\nProduct #\d+:|$))',
                    result_text,
                    re.DOTALL,
                )

                if not products:
                    await update.message.reply_text("⚠️ Unexpected response format.")
                    return

                reply_lines = [f"🔍 Found: {len(products)} product{'s' if len(products) > 1 else ''}"]
                for num, name, price, description in products:
                    reply_lines.append(
                        f"\n🔔 Product #{num}\n"
                        f"🛍 Name: {name.strip()}\n"
                        f"💰 Price: {price.strip()}\n"
                        f"📄 Description: {description.strip()}"
                    )
                set_user_state(user_id, None)
                await update.message.reply_text("\n".join(reply_lines))
            else:
                await update.message.reply_text(f"❌ Search error: {response.text}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error during search:\n{e}")
        return

    if state == 'subscribe':

        try:
            seller_id = int(text)
        except ValueError:
            await update.message.reply_text("❌ Seller ID must be an integer. Try again:")
            return

        try:
            response = requests.post(
                f"http://{backend_host}:5000/subscriptions/subscribe/{seller_id}",
                headers={"Authorization": f"Bearer {jwt_token}"},
            )
            if response.status_code in (200, 201):
                data = response.json()
                await update.message.reply_text(f"✅ {data.get('message', 'Subscribed successfully.')}")
            else:
                data = response.json()
                error_msg = data.get("error") or response.text
                await update.message.reply_text(f"❌ Failed to subscribe: {error_msg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error during subscription:\n{e}")

        set_user_state(user_id, None)
        return

    if state == 'unsubscribe':

        try:
            seller_id = int(text)
        except ValueError:
            await update.message.reply_text("❌ Seller ID must be an integer. Try again:")
            return

        try:
            response = requests.post(
                f"http://{backend_host}:5000/subscriptions/unsubscribe/{seller_id}",
                headers={"Authorization": f"Bearer {jwt_token}"},
            )
            if response.status_code == 200:
                data = response.json()
                await update.message.reply_text(f"✅ {data.get('message', 'Unsubscribed successfully.')}")
            else:
                data = response.json()
                error_msg = data.get("error") or response.text
                await update.message.reply_text(f"❌ Failed to unsubscribe: {error_msg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error during unsubscription:\n{e}")

        set_user_state(user_id, None)
        return

    if state == "create_product":

            parts = [p.strip() for p in text.split(",")]
            if len(parts) < 2:
                await update.message.reply_text("❌ Invalid format. Use: name; price; description (description optional)")
                return
            name = parts[0]
            try:
                price = float(parts[1])
            except ValueError:
                await update.message.reply_text("❌ Price must be a number.")
                return
            description = parts[2] if len(parts) > 2 else ""

            payload = {"name": name, "price": price, "description": description}
            try:
                response = requests.post(f"http://{backend_host}:5000/products", json=payload, headers=headers)
                if response.status_code == 201:
                    product = response.json()
                    await update.message.reply_text(f"✅ Product created with ID #{product.get('id')}")
                    set_user_state(user_id, None)
                else:
                    await update.message.reply_text(f"❌ Failed to create product: {response.text}")
            except Exception as e:
                await update.message.reply_text(f"⚠️ Error creating product:\n{e}")
            return

    if state == "get_product_detail":

        try:
            product_id = int(text)
        except ValueError:
            await update.message.reply_text("❌ Product ID must be an integer.")
            return
        try:
            response = requests.get(
                f"http://{backend_host}:5000/products/{product_id}",
                headers=headers
            )
            if response.status_code == 200:
                p = response.json()
                msg = (
                    f"🔍 Product #{p.get('id')}\n"
                    f"🛍 Name: {p.get('name')}\n"
                    f"💰 Price: {p.get('price')}\n"
                    f"📄 Description: {p.get('description') or 'No description'}\n"
                    f"💵 Sold: {'Yes' if p.get('is_sold') else 'No'}"
                )
                await update.message.reply_text(msg)
                set_user_state(user_id, None)
            else:
                await update.message.reply_text(f"❌ Product not found: {response.text}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error fetching product:\n{e}")
        return

    if state == "update_product_ask_id":

        try:
            product_id = int(text)
        except ValueError:
            await update.message.reply_text("❌ Product ID must be an integer.")
            return
        context.user_data['update_product_id'] = product_id
        set_user_state(user_id, "update_product_ask_fields")
        await update.message.reply_text(
            "✏️ Enter fields to update in format:\n"
            "name, price, description\n"
            "Leave field empty to skip (e.g. , 100.0, new description)"
        )
        return

    if state == "update_product_ask_fields":

        product_id = context.user_data.get('update_product_id')
        if not product_id:
            await update.message.reply_text("❌ Internal error: product ID not found in context.")
            set_user_state(user_id, None)
            return

        parts = [p.strip() for p in text.split(",")]
        name = parts[0] if len(parts) > 0 and parts[0] else None
        price = None
        if len(parts) > 1 and parts[1]:
            try:
                price = float(parts[1])
            except ValueError:
                await update.message.reply_text("❌ Price must be a number.")
                return
        description = parts[2] if len(parts) > 2 and parts[2] else None

        payload = {}
        if name is not None:
            payload['name'] = name
        if price is not None:
            payload['price'] = price
        if description is not None:
            payload['description'] = description

        if not payload:
            await update.message.reply_text("❌ No fields provided for update.")
            return

        try:
            response = requests.patch(
                f"http://{backend_host}:5000/products/{product_id}",
                json=payload,
                headers=headers
            )
            if response.status_code == 200:
                product = response.json()
                await update.message.reply_text(f"✅ Product updated: #{product.get('id')} {product.get('name')}")
                set_user_state(user_id, None)
                context.user_data.pop('update_product_id', None)
            elif response.status_code == 403:
                await update.message.reply_text("❌ Forbidden: You are not the seller of this product.")
            else:
                await update.message.reply_text(f"❌ Failed to update product: {response.text}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error updating product:\n{e}")
        return

    if state == "delete_product":

        try:
            product_id = int(text)
        except ValueError:
            await update.message.reply_text("❌ Product ID must be an integer.")
            return

        try:
            response = requests.delete(
                f"http://{backend_host}:5000/products/{product_id}",
                headers=headers
            )
            if response.status_code == 200:
                await update.message.reply_text("✅ Product deleted successfully.")
                set_user_state(user_id, None)
            elif response.status_code == 403:
                await update.message.reply_text("❌ Forbidden: You are not the seller of this product.")
            elif response.status_code == 404:
                await update.message.reply_text("❌ Product not found.")
            else:
                await update.message.reply_text(f"❌ Failed to delete product: {response.text}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error deleting product:\n{e}")
        return

    if state == "purchase_product":

        try:
            product_id = int(text)
        except ValueError:
            await update.message.reply_text("❌ Product ID must be an integer.")
            return

        try:
            response = requests.post(
                f"http://{backend_host}:5000/products/purchase/{product_id}",
                headers=headers
            )
            if response.status_code == 200:
                await update.message.reply_text("✅ Purchase successful!")
                set_user_state(user_id, None)
            elif response.status_code == 400:
                await update.message.reply_text(f"❌ Bad request: {response.json().get('error')}")
            elif response.status_code == 404:
                await update.message.reply_text("❌ Product not found.")
            else:
                await update.message.reply_text(f"❌ Failed to purchase product: {response.text}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error purchasing product:\n{e}")
        return

    await update.message.reply_text("❓ Please use buttons or commands from the menu.")

def register_handlers(application):

    """Register bot command and message handlers."""

    from telegram.ext import CommandHandler, MessageHandler, filters

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
