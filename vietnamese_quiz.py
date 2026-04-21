import random
import json
import os
import tempfile
from datetime import date, datetime
from difflib import SequenceMatcher

# Text-to-speech support
TTS_AVAILABLE = False
TTS_ERROR = ""
try:
    from gtts import gTTS
    import pygame
    pygame.mixer.init()
    TTS_AVAILABLE = True
except Exception as e:
    TTS_ERROR = f"{type(e).__name__}: {e}"


PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vietnamese_progress.json")
SIMILARITY_THRESHOLD = 0.8


def speak_vietnamese(text):
    """Play Vietnamese text-to-speech audio"""
    if not TTS_AVAILABLE:
        print(f"  [Audio unavailable — {TTS_ERROR}]")
        print("  [Install with: pip install gTTS pygame  (use the same Python you're running)]")
        return
    tmp_path = None
    try:
        tts = gTTS(text=text, lang='vi')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            tmp_path = f.name
        tts.save(tmp_path)
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(50)
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"  [Audio error: {type(e).__name__}: {e}]")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


# Vietnamese vocabulary database (Southern accent pronunciations)
# Each entry: vietnamese, english (primary), pronunciation, accept (optional list of extra acceptable answers)
vocabulary = {
    "numbers": [
        {"vietnamese": "Không", "english": "Zero", "pronunciation": "khom", "accept": ["0"]},
        {"vietnamese": "Một", "english": "One", "pronunciation": "moht", "accept": ["1"]},
        {"vietnamese": "Hai", "english": "Two", "pronunciation": "hai", "accept": ["2"]},
        {"vietnamese": "Ba", "english": "Three", "pronunciation": "ba", "accept": ["3"]},
        {"vietnamese": "Bốn", "english": "Four", "pronunciation": "bohn", "accept": ["4"]},
        {"vietnamese": "Năm", "english": "Five", "pronunciation": "nam", "accept": ["5"]},
        {"vietnamese": "Sáu", "english": "Six", "pronunciation": "shaow", "accept": ["6"]},
        {"vietnamese": "Bảy", "english": "Seven", "pronunciation": "bay", "accept": ["7"]},
        {"vietnamese": "Tám", "english": "Eight", "pronunciation": "tahm", "accept": ["8"]},
        {"vietnamese": "Chín", "english": "Nine", "pronunciation": "chin", "accept": ["9"]},
        {"vietnamese": "Mười", "english": "Ten", "pronunciation": "muey", "accept": ["10"]},
        {"vietnamese": "Mười một", "english": "Eleven", "pronunciation": "muey moht", "accept": ["11"]},
        {"vietnamese": "Mười hai", "english": "Twelve", "pronunciation": "muey hai", "accept": ["12"]},
        {"vietnamese": "Mười lăm", "english": "Fifteen", "pronunciation": "muey lam", "accept": ["15"]},
        {"vietnamese": "Hai mươi", "english": "Twenty", "pronunciation": "hai muey", "accept": ["20"]},
        {"vietnamese": "Ba mươi", "english": "Thirty", "pronunciation": "ba muey", "accept": ["30"]},
        {"vietnamese": "Năm mươi", "english": "Fifty", "pronunciation": "nam muey", "accept": ["50"]},
        {"vietnamese": "Một trăm", "english": "One hundred", "pronunciation": "moht cham", "accept": ["100", "hundred"]},
        {"vietnamese": "Một nghìn", "english": "One thousand", "pronunciation": "moht ngin", "accept": ["1000", "thousand", "một ngàn"]},
    ],
    "addressing": [
        {"vietnamese": "Em", "english": "Younger person", "pronunciation": "em",
         "accept": ["younger", "young person", "little sibling", "younger sibling"]},
        {"vietnamese": "Anh", "english": "Older brother / older man around your age", "pronunciation": "ahn",
         "accept": ["older brother", "big brother", "older male", "older guy"]},
        {"vietnamese": "Chị", "english": "Older sister / older woman around your age", "pronunciation": "chee",
         "accept": ["older sister", "big sister", "older female", "older woman"]},
        {"vietnamese": "Bạn", "english": "Friend (same age)", "pronunciation": "bahn",
         "accept": ["friend", "same age", "you (friend)"]},
        {"vietnamese": "Chú", "english": "Uncle / man around your dad's age", "pronunciation": "choo",
         "accept": ["uncle", "mr", "middle aged man", "dads age", "older man"]},
        {"vietnamese": "Cô", "english": "Aunt / woman around your mom's age (also teacher)", "pronunciation": "koh",
         "accept": ["aunt", "ms", "teacher", "middle aged woman", "moms age", "older woman"]},
        {"vietnamese": "Bác", "english": "Older uncle/aunt (older than your parents)", "pronunciation": "bak",
         "accept": ["older uncle", "older aunt", "older than parents", "elder"]},
        {"vietnamese": "Ông", "english": "Grandfather / elderly man / Mr.", "pronunciation": "ohm",
         "accept": ["grandfather", "grandpa", "old man", "elderly man", "mr", "sir"]},
        {"vietnamese": "Bà", "english": "Grandmother / elderly woman / Mrs.", "pronunciation": "ba",
         "accept": ["grandmother", "grandma", "old woman", "elderly woman", "mrs", "maam"]},
        {"vietnamese": "Cháu", "english": "Young person (to elder) / grandchild", "pronunciation": "chow",
         "accept": ["grandchild", "young to elder", "niece", "nephew"]},
        {"vietnamese": "Con", "english": "Child (parent to child, or child to parent)", "pronunciation": "kon",
         "accept": ["child", "son", "daughter", "kid"]},
        {"vietnamese": "Tôi", "english": "I / me (formal, neutral)", "pronunciation": "toy",
         "accept": ["i", "me", "formal i"]},
        {"vietnamese": "Mình", "english": "I / me (casual, with friends)", "pronunciation": "ming",
         "accept": ["casual i", "me casual", "i friends"]},
    ],
    "ordering": [
        {"vietnamese": "Xin chào", "english": "Hello", "pronunciation": "sin chow", "accept": ["hi", "hey"]},
        {"vietnamese": "Tôi muốn...", "english": "I want...", "pronunciation": "toy muohn",
         "accept": ["i want", "want", "id like"]},
        {"vietnamese": "Cho tôi...", "english": "Give me...", "pronunciation": "cho toy",
         "accept": ["give me", "can i have", "ill have"]},
        {"vietnamese": "Bao nhiêu tiền?", "english": "How much?", "pronunciation": "bow nyew tee-en",
         "accept": ["how much", "price", "cost", "how much money"]},
        {"vietnamese": "Cảm ơn", "english": "Thank you", "pronunciation": "kahm uhn",
         "accept": ["thanks", "ty", "thx"]},
        {"vietnamese": "Không có vấn đề", "english": "No problem", "pronunciation": "khom co yun deh",
         "accept": ["np", "no worries", "youre welcome"]},
        {"vietnamese": "Tính tiền", "english": "Check please (the bill)", "pronunciation": "ting tee-en",
         "accept": ["check", "bill", "the bill", "check please"]},
        {"vietnamese": "Ngon quá", "english": "Very delicious", "pronunciation": "ngon kwa",
         "accept": ["delicious", "tasty", "yummy", "so good"]},
        {"vietnamese": "Cay", "english": "Spicy", "pronunciation": "kai", "accept": ["hot"]},
        {"vietnamese": "Không cay", "english": "Not spicy", "pronunciation": "khom kai",
         "accept": ["no spice", "mild", "not hot"]},
        {"vietnamese": "Thêm", "english": "More / add more", "pronunciation": "tem",
         "accept": ["more", "add more", "extra"]},
        {"vietnamese": "Đá", "english": "Ice", "pronunciation": "da", "accept": []},
        {"vietnamese": "Không đá", "english": "No ice", "pronunciation": "khom da",
         "accept": ["no ice"]},
        {"vietnamese": "Đem đi", "english": "Take away / to go", "pronunciation": "dem dee",
         "accept": ["to go", "takeaway", "take out"]},
        {"vietnamese": "Ăn ở đây", "english": "Eat here / dine in", "pronunciation": "an uh day",
         "accept": ["eat here", "dine in", "for here"]},
    ],
    "daily": [
        {"vietnamese": "Chào buổi sáng", "english": "Good morning", "pronunciation": "chow buoy shahng",
         "accept": ["morning", "gm"]},
        {"vietnamese": "Chào buổi tối", "english": "Good evening", "pronunciation": "chow buoy toy",
         "accept": ["evening", "good night"]},
        {"vietnamese": "Bạn khỏe không?", "english": "How are you?", "pronunciation": "bahn kweh khom",
         "accept": ["how r u", "hows it going", "you good"]},
        {"vietnamese": "Tôi khỏe, cảm ơn", "english": "I'm fine, thank you", "pronunciation": "toy kweh kahm uhn",
         "accept": ["im fine", "im good", "good thanks", "im well"]},
        {"vietnamese": "Bạn tên gì?", "english": "What's your name?", "pronunciation": "bahn ten yi",
         "accept": ["your name", "whats ur name", "name"]},
        {"vietnamese": "Tôi tên là...", "english": "My name is...", "pronunciation": "toy ten la",
         "accept": ["my name", "im called", "im"]},
        {"vietnamese": "Xin lỗi", "english": "Excuse me / Sorry", "pronunciation": "sin loy",
         "accept": ["sorry", "excuse me", "my bad"]},
        {"vietnamese": "Tạm biệt", "english": "Goodbye", "pronunciation": "tahm bee-yet",
         "accept": ["bye", "see ya", "cya"]},
        {"vietnamese": "Hẹn gặp lại", "english": "See you again", "pronunciation": "hen gahp lai",
         "accept": ["see you later", "see u", "later"]},
        {"vietnamese": "Vâng / Dạ", "english": "Yes (polite)", "pronunciation": "vung / ya",
         "accept": ["yes", "yeah", "yep"]},
        {"vietnamese": "Không", "english": "No", "pronunciation": "khom",
         "accept": ["nope", "nah"]},
        {"vietnamese": "Có", "english": "Yes / have", "pronunciation": "co",
         "accept": ["yes", "have"]},
        {"vietnamese": "Tôi không hiểu", "english": "I don't understand", "pronunciation": "toy khom hyew",
         "accept": ["dont understand", "no understand", "i dont get it"]},
        {"vietnamese": "Bạn nói tiếng Anh không?", "english": "Do you speak English?", "pronunciation": "bahn noy tee-eng ahn khom",
         "accept": ["speak english", "do you speak english", "english?"]},
        {"vietnamese": "Nói chậm lại", "english": "Please speak slower", "pronunciation": "noy chum lai",
         "accept": ["speak slower", "slower", "slow down"]},
        {"vietnamese": "Làm ơn", "english": "Please", "pronunciation": "lam uhn",
         "accept": ["plz", "pls"]},
        {"vietnamese": "Chúc mừng", "english": "Congratulations", "pronunciation": "chook moong",
         "accept": ["congrats", "congratulations"]},
        {"vietnamese": "Tôi yêu bạn", "english": "I love you", "pronunciation": "toy yew bahn",
         "accept": ["love you", "ily"]},
    ],
    "food": [
        {"vietnamese": "Nước", "english": "Water", "pronunciation": "nuoc", "accept": []},
        {"vietnamese": "Cà phê", "english": "Coffee", "pronunciation": "ka feh",
         "accept": ["caffe"]},
        {"vietnamese": "Cà phê sữa đá", "english": "Iced coffee with milk", "pronunciation": "ka feh sua da",
         "accept": ["iced milk coffee", "vietnamese iced coffee"]},
        {"vietnamese": "Trà", "english": "Tea", "pronunciation": "cha", "accept": []},
        {"vietnamese": "Trà đá", "english": "Iced tea", "pronunciation": "cha da",
         "accept": ["iced tea"]},
        {"vietnamese": "Bia", "english": "Beer", "pronunciation": "bee-a", "accept": []},
        {"vietnamese": "Cơm", "english": "Rice", "pronunciation": "kuhm", "accept": []},
        {"vietnamese": "Phở", "english": "Pho (noodle soup)", "pronunciation": "fuh",
         "accept": ["pho", "noodle soup"]},
        {"vietnamese": "Bánh mì", "english": "Banh mi (sandwich)", "pronunciation": "bahn mee",
         "accept": ["sandwich", "banh mi", "bread"]},
        {"vietnamese": "Bún", "english": "Rice vermicelli noodles", "pronunciation": "boon",
         "accept": ["vermicelli", "noodles", "rice noodles"]},
        {"vietnamese": "Gỏi cuốn", "english": "Fresh spring rolls", "pronunciation": "goy kuon",
         "accept": ["spring rolls", "summer rolls", "fresh rolls"]},
        {"vietnamese": "Chả giò", "english": "Fried spring rolls", "pronunciation": "cha yo",
         "accept": ["fried rolls", "egg rolls"]},
        {"vietnamese": "Gà", "english": "Chicken", "pronunciation": "ga", "accept": []},
        {"vietnamese": "Bò", "english": "Beef", "pronunciation": "bo", "accept": []},
        {"vietnamese": "Heo / Lợn", "english": "Pork", "pronunciation": "hey-o / lohn",
         "accept": ["pork", "pig"]},
        {"vietnamese": "Cá", "english": "Fish", "pronunciation": "ka", "accept": []},
        {"vietnamese": "Tôm", "english": "Shrimp", "pronunciation": "tom", "accept": ["prawn"]},
        {"vietnamese": "Rau", "english": "Vegetables", "pronunciation": "raow",
         "accept": ["veggies", "greens", "herbs"]},
        {"vietnamese": "Trái cây", "english": "Fruit", "pronunciation": "chai kai", "accept": []},
        {"vietnamese": "Tráng miệng", "english": "Dessert", "pronunciation": "chahng mee-eng",
         "accept": ["sweets"]},
        {"vietnamese": "Bạn thích ăn gì?", "english": "What do you like to eat?", "pronunciation": "bahn thik an yi",
         "accept": ["what do you like to eat", "what you eat", "favorite food"]},
        {"vietnamese": "Đói", "english": "Hungry", "pronunciation": "doy", "accept": ["im hungry"]},
        {"vietnamese": "Khát", "english": "Thirsty", "pronunciation": "khat", "accept": ["im thirsty"]},
        {"vietnamese": "No", "english": "Full (not hungry)", "pronunciation": "no",
         "accept": ["full", "stuffed"]},
    ],
    "family": [
        {"vietnamese": "Gia đình", "english": "Family", "pronunciation": "ya ding", "accept": []},
        {"vietnamese": "Bố / Ba", "english": "Father / Dad", "pronunciation": "bo / ba",
         "accept": ["father", "dad", "papa"]},
        {"vietnamese": "Mẹ / Má", "english": "Mother / Mom", "pronunciation": "me / ma",
         "accept": ["mother", "mom", "mama"]},
        {"vietnamese": "Con trai", "english": "Son", "pronunciation": "kon chai",
         "accept": ["boy", "son"]},
        {"vietnamese": "Con gái", "english": "Daughter", "pronunciation": "kon gai",
         "accept": ["girl", "daughter"]},
        {"vietnamese": "Anh trai", "english": "Older brother", "pronunciation": "ahn chai",
         "accept": ["older brother", "big brother"]},
        {"vietnamese": "Chị gái", "english": "Older sister", "pronunciation": "chee gai",
         "accept": ["older sister", "big sister"]},
        {"vietnamese": "Em trai", "english": "Younger brother", "pronunciation": "em chai",
         "accept": ["younger brother", "little brother"]},
        {"vietnamese": "Em gái", "english": "Younger sister", "pronunciation": "em gai",
         "accept": ["younger sister", "little sister"]},
        {"vietnamese": "Vợ", "english": "Wife", "pronunciation": "vuh", "accept": []},
        {"vietnamese": "Chồng", "english": "Husband", "pronunciation": "chohm", "accept": []},
        {"vietnamese": "Bạn trai", "english": "Boyfriend", "pronunciation": "bahn chai", "accept": ["bf"]},
        {"vietnamese": "Bạn gái", "english": "Girlfriend", "pronunciation": "bahn gai", "accept": ["gf"]},
    ],
    "time": [
        {"vietnamese": "Hôm nay", "english": "Today", "pronunciation": "hohm nai", "accept": []},
        {"vietnamese": "Hôm qua", "english": "Yesterday", "pronunciation": "hohm kwa", "accept": []},
        {"vietnamese": "Ngày mai", "english": "Tomorrow", "pronunciation": "ngai mai", "accept": []},
        {"vietnamese": "Bây giờ", "english": "Now", "pronunciation": "bay yuh", "accept": ["right now"]},
        {"vietnamese": "Sau", "english": "Later / after", "pronunciation": "shaow",
         "accept": ["later", "after"]},
        {"vietnamese": "Thứ Hai", "english": "Monday", "pronunciation": "too hai", "accept": ["mon"]},
        {"vietnamese": "Thứ Ba", "english": "Tuesday", "pronunciation": "too ba", "accept": ["tue"]},
        {"vietnamese": "Thứ Tư", "english": "Wednesday", "pronunciation": "too too", "accept": ["wed"]},
        {"vietnamese": "Thứ Năm", "english": "Thursday", "pronunciation": "too nam", "accept": ["thu"]},
        {"vietnamese": "Thứ Sáu", "english": "Friday", "pronunciation": "too shaow", "accept": ["fri"]},
        {"vietnamese": "Thứ Bảy", "english": "Saturday", "pronunciation": "too bay", "accept": ["sat"]},
        {"vietnamese": "Chủ Nhật", "english": "Sunday", "pronunciation": "choo nyut", "accept": ["sun"]},
        {"vietnamese": "Sáng", "english": "Morning", "pronunciation": "shahng", "accept": ["am"]},
        {"vietnamese": "Chiều", "english": "Afternoon", "pronunciation": "chyew", "accept": ["pm"]},
        {"vietnamese": "Tối", "english": "Night / evening", "pronunciation": "toy",
         "accept": ["night", "evening"]},
    ],
    "directions": [
        {"vietnamese": "Ở đâu?", "english": "Where?", "pronunciation": "uh dow", "accept": ["where"]},
        {"vietnamese": "Bên trái", "english": "Left", "pronunciation": "ben chai", "accept": []},
        {"vietnamese": "Bên phải", "english": "Right", "pronunciation": "ben fai", "accept": []},
        {"vietnamese": "Thẳng", "english": "Straight", "pronunciation": "tahng",
         "accept": ["straight ahead", "go straight"]},
        {"vietnamese": "Gần", "english": "Near / close", "pronunciation": "gun",
         "accept": ["near", "close"]},
        {"vietnamese": "Xa", "english": "Far", "pronunciation": "sa", "accept": []},
        {"vietnamese": "Ở đây", "english": "Here", "pronunciation": "uh day", "accept": []},
        {"vietnamese": "Ở kia", "english": "There", "pronunciation": "uh kya", "accept": []},
        {"vietnamese": "Nhà vệ sinh", "english": "Bathroom / toilet", "pronunciation": "nya veh shing",
         "accept": ["toilet", "restroom", "bathroom", "wc"]},
        {"vietnamese": "Khách sạn", "english": "Hotel", "pronunciation": "khak shan", "accept": []},
        {"vietnamese": "Sân bay", "english": "Airport", "pronunciation": "shun bay", "accept": []},
    ],
    "common_verbs": [
        {"vietnamese": "Đi", "english": "To go", "pronunciation": "dee", "accept": ["go"]},
        {"vietnamese": "Đến", "english": "To come / arrive", "pronunciation": "den", "accept": ["come", "arrive"]},
        {"vietnamese": "Ăn", "english": "To eat", "pronunciation": "an", "accept": ["eat"]},
        {"vietnamese": "Uống", "english": "To drink", "pronunciation": "uohng", "accept": ["drink"]},
        {"vietnamese": "Ngủ", "english": "To sleep", "pronunciation": "ngoo", "accept": ["sleep"]},
        {"vietnamese": "Làm", "english": "To do / make", "pronunciation": "lam", "accept": ["do", "make"]},
        {"vietnamese": "Muốn", "english": "To want", "pronunciation": "muohn", "accept": ["want"]},
        {"vietnamese": "Cần", "english": "To need", "pronunciation": "kun", "accept": ["need"]},
        {"vietnamese": "Thích", "english": "To like", "pronunciation": "thik", "accept": ["like"]},
        {"vietnamese": "Biết", "english": "To know", "pronunciation": "byet", "accept": ["know"]},
        {"vietnamese": "Hiểu", "english": "To understand", "pronunciation": "hyew", "accept": ["understand", "get it"]},
        {"vietnamese": "Nói", "english": "To speak / say / talk", "pronunciation": "noy", "accept": ["speak", "say", "talk"]},
        {"vietnamese": "Nghe", "english": "To listen / hear", "pronunciation": "nge", "accept": ["listen", "hear"]},
        {"vietnamese": "Xem", "english": "To watch / look at", "pronunciation": "sem", "accept": ["watch", "look"]},
        {"vietnamese": "Thấy", "english": "To see", "pronunciation": "thay", "accept": ["see"]},
        {"vietnamese": "Đọc", "english": "To read", "pronunciation": "dok", "accept": ["read"]},
        {"vietnamese": "Viết", "english": "To write", "pronunciation": "vyet", "accept": ["write"]},
        {"vietnamese": "Học", "english": "To learn / study", "pronunciation": "hok", "accept": ["learn", "study"]},
        {"vietnamese": "Làm việc", "english": "To work", "pronunciation": "lam vyek", "accept": ["work"]},
        {"vietnamese": "Mua", "english": "To buy", "pronunciation": "mua", "accept": ["buy", "purchase"]},
        {"vietnamese": "Bán", "english": "To sell", "pronunciation": "ban", "accept": ["sell"]},
        {"vietnamese": "Nghĩ", "english": "To think", "pronunciation": "ngee", "accept": ["think"]},
        {"vietnamese": "Nhớ", "english": "To remember / miss", "pronunciation": "nyuh", "accept": ["remember", "miss"]},
        {"vietnamese": "Quên", "english": "To forget", "pronunciation": "kwen", "accept": ["forget"]},
        {"vietnamese": "Giúp", "english": "To help", "pronunciation": "yup", "accept": ["help"]},
        {"vietnamese": "Chơi", "english": "To play / hang out", "pronunciation": "choy", "accept": ["play", "hang out"]},
        {"vietnamese": "Nấu ăn", "english": "To cook", "pronunciation": "nau an", "accept": ["cook"]},
        {"vietnamese": "Chạy", "english": "To run", "pronunciation": "chai", "accept": ["run"]},
        {"vietnamese": "Đợi", "english": "To wait", "pronunciation": "doy", "accept": ["wait"]},
        {"vietnamese": "Ở", "english": "To stay / live / be at", "pronunciation": "uh", "accept": ["stay", "live", "be at"]},
        {"vietnamese": "Tìm", "english": "To look for / find", "pronunciation": "tim", "accept": ["find", "look for", "search"]},
        {"vietnamese": "Đưa", "english": "To give / hand over", "pronunciation": "dua", "accept": ["give", "hand", "pass"]},
    ],
    "adjectives": [
        {"vietnamese": "Lớn / To", "english": "Big / large", "pronunciation": "luhn / to", "accept": ["big", "large"]},
        {"vietnamese": "Nhỏ", "english": "Small", "pronunciation": "nyo", "accept": ["small", "little", "tiny"]},
        {"vietnamese": "Nóng", "english": "Hot", "pronunciation": "nohng", "accept": ["hot"]},
        {"vietnamese": "Lạnh", "english": "Cold", "pronunciation": "lahn", "accept": ["cold"]},
        {"vietnamese": "Ấm", "english": "Warm", "pronunciation": "um", "accept": ["warm"]},
        {"vietnamese": "Mát", "english": "Cool", "pronunciation": "mat", "accept": ["cool"]},
        {"vietnamese": "Tốt", "english": "Good", "pronunciation": "toht", "accept": ["good", "nice"]},
        {"vietnamese": "Xấu", "english": "Bad / ugly", "pronunciation": "sow", "accept": ["bad", "ugly"]},
        {"vietnamese": "Đẹp", "english": "Beautiful / pretty", "pronunciation": "dep", "accept": ["beautiful", "pretty", "nice looking"]},
        {"vietnamese": "Mới", "english": "New", "pronunciation": "muey", "accept": ["new"]},
        {"vietnamese": "Cũ", "english": "Old (things)", "pronunciation": "koo", "accept": ["old", "used"]},
        {"vietnamese": "Già", "english": "Old (people)", "pronunciation": "ya", "accept": ["old", "elderly"]},
        {"vietnamese": "Trẻ", "english": "Young", "pronunciation": "che", "accept": ["young"]},
        {"vietnamese": "Nhanh", "english": "Fast / quick", "pronunciation": "nyahn", "accept": ["fast", "quick"]},
        {"vietnamese": "Chậm", "english": "Slow", "pronunciation": "chum", "accept": ["slow"]},
        {"vietnamese": "Dễ", "english": "Easy", "pronunciation": "ye", "accept": ["easy", "simple"]},
        {"vietnamese": "Khó", "english": "Hard / difficult", "pronunciation": "kho", "accept": ["hard", "difficult"]},
        {"vietnamese": "Đắt / Mắc", "english": "Expensive", "pronunciation": "dut / mak", "accept": ["expensive", "pricey"]},
        {"vietnamese": "Rẻ", "english": "Cheap", "pronunciation": "reh", "accept": ["cheap", "inexpensive"]},
        {"vietnamese": "Cao", "english": "Tall / high", "pronunciation": "cao", "accept": ["tall", "high"]},
        {"vietnamese": "Thấp", "english": "Short / low", "pronunciation": "thup", "accept": ["short", "low"]},
        {"vietnamese": "Sạch", "english": "Clean", "pronunciation": "sak", "accept": ["clean"]},
        {"vietnamese": "Bẩn", "english": "Dirty", "pronunciation": "bun", "accept": ["dirty"]},
        {"vietnamese": "Đông", "english": "Crowded", "pronunciation": "dohng", "accept": ["crowded", "busy place"]},
        {"vietnamese": "Vắng", "english": "Empty / deserted", "pronunciation": "vahng", "accept": ["empty", "deserted"]},
        {"vietnamese": "Nặng", "english": "Heavy", "pronunciation": "nahng", "accept": ["heavy"]},
        {"vietnamese": "Nhẹ", "english": "Light (weight)", "pronunciation": "nye", "accept": ["light"]},
        {"vietnamese": "Dài", "english": "Long", "pronunciation": "yai", "accept": ["long"]},
        {"vietnamese": "Ngắn", "english": "Short (length)", "pronunciation": "ngahn", "accept": ["short"]},
    ],
    "questions": [
        {"vietnamese": "Gì?", "english": "What?", "pronunciation": "yi", "accept": ["what"]},
        {"vietnamese": "Cái gì?", "english": "What is it? / what thing?", "pronunciation": "kai yi", "accept": ["what is it", "what thing", "what"]},
        {"vietnamese": "Khi nào?", "english": "When?", "pronunciation": "khee now", "accept": ["when"]},
        {"vietnamese": "Tại sao?", "english": "Why?", "pronunciation": "tai sao", "accept": ["why", "how come"]},
        {"vietnamese": "Như thế nào?", "english": "How? (in what way)", "pronunciation": "nyu teh now", "accept": ["how", "in what way"]},
        {"vietnamese": "Ai?", "english": "Who?", "pronunciation": "ai", "accept": ["who"]},
        {"vietnamese": "Của ai?", "english": "Whose?", "pronunciation": "kua ai", "accept": ["whose"]},
        {"vietnamese": "Cái nào?", "english": "Which one?", "pronunciation": "kai now", "accept": ["which", "which one"]},
        {"vietnamese": "Mấy?", "english": "How many? (small numbers)", "pronunciation": "may", "accept": ["how many"]},
        {"vietnamese": "Bao nhiêu?", "english": "How much / how many?", "pronunciation": "bow nyew", "accept": ["how much", "how many"]},
        {"vietnamese": "Bao lâu?", "english": "How long? (time)", "pronunciation": "bow low", "accept": ["how long"]},
    ],
    "colors": [
        {"vietnamese": "Màu đỏ", "english": "Red", "pronunciation": "mau do", "accept": ["red"]},
        {"vietnamese": "Màu xanh dương", "english": "Blue", "pronunciation": "mau sahn yuohng", "accept": ["blue"]},
        {"vietnamese": "Màu xanh lá", "english": "Green", "pronunciation": "mau sahn la", "accept": ["green"]},
        {"vietnamese": "Màu vàng", "english": "Yellow", "pronunciation": "mau vahng", "accept": ["yellow", "gold"]},
        {"vietnamese": "Màu đen", "english": "Black", "pronunciation": "mau den", "accept": ["black"]},
        {"vietnamese": "Màu trắng", "english": "White", "pronunciation": "mau chahng", "accept": ["white"]},
        {"vietnamese": "Màu cam", "english": "Orange", "pronunciation": "mau kam", "accept": ["orange"]},
        {"vietnamese": "Màu hồng", "english": "Pink", "pronunciation": "mau hohng", "accept": ["pink"]},
        {"vietnamese": "Màu nâu", "english": "Brown", "pronunciation": "mau nau", "accept": ["brown"]},
        {"vietnamese": "Màu tím", "english": "Purple", "pronunciation": "mau tim", "accept": ["purple", "violet"]},
        {"vietnamese": "Màu xám", "english": "Gray", "pronunciation": "mau sam", "accept": ["gray", "grey"]},
    ],
    "places": [
        {"vietnamese": "Nhà", "english": "Home / house", "pronunciation": "nya", "accept": ["home", "house"]},
        {"vietnamese": "Chợ", "english": "Market", "pronunciation": "chuh", "accept": ["market"]},
        {"vietnamese": "Siêu thị", "english": "Supermarket", "pronunciation": "shew thee", "accept": ["supermarket", "grocery store"]},
        {"vietnamese": "Cửa hàng", "english": "Store / shop", "pronunciation": "kua hahng", "accept": ["store", "shop"]},
        {"vietnamese": "Nhà hàng", "english": "Restaurant", "pronunciation": "nya hahng", "accept": ["restaurant"]},
        {"vietnamese": "Quán cà phê", "english": "Coffee shop", "pronunciation": "kwan ka feh", "accept": ["coffee shop", "cafe"]},
        {"vietnamese": "Quán nhậu", "english": "Bar / drinking spot", "pronunciation": "kwan nyow", "accept": ["bar", "pub", "drinking spot"]},
        {"vietnamese": "Bệnh viện", "english": "Hospital", "pronunciation": "ben vyen", "accept": ["hospital"]},
        {"vietnamese": "Ngân hàng", "english": "Bank", "pronunciation": "ngun hahng", "accept": ["bank"]},
        {"vietnamese": "Trường học", "english": "School", "pronunciation": "chuhng hok", "accept": ["school"]},
        {"vietnamese": "Công viên", "english": "Park", "pronunciation": "kong vyen", "accept": ["park"]},
        {"vietnamese": "Chùa", "english": "Buddhist temple / pagoda", "pronunciation": "chua", "accept": ["temple", "pagoda", "buddhist temple"]},
        {"vietnamese": "Nhà thờ", "english": "Church", "pronunciation": "nya thuh", "accept": ["church"]},
        {"vietnamese": "Biển", "english": "Beach / sea", "pronunciation": "byen", "accept": ["beach", "sea", "ocean"]},
        {"vietnamese": "Núi", "english": "Mountain", "pronunciation": "nuy", "accept": ["mountain", "hill"]},
        {"vietnamese": "Thành phố", "english": "City", "pronunciation": "thahn foh", "accept": ["city", "town"]},
        {"vietnamese": "Quê", "english": "Hometown / countryside", "pronunciation": "kweh", "accept": ["hometown", "countryside", "village"]},
    ],
    "transportation": [
        {"vietnamese": "Xe máy", "english": "Motorbike / scooter", "pronunciation": "se mai", "accept": ["motorbike", "scooter", "moped"]},
        {"vietnamese": "Xe hơi / Ô tô", "english": "Car", "pronunciation": "se huy / oh toh", "accept": ["car", "auto"]},
        {"vietnamese": "Xe buýt", "english": "Bus", "pronunciation": "se bweet", "accept": ["bus"]},
        {"vietnamese": "Xe đạp", "english": "Bicycle", "pronunciation": "se dap", "accept": ["bicycle", "bike"]},
        {"vietnamese": "Taxi", "english": "Taxi", "pronunciation": "tak si", "accept": ["taxi", "cab"]},
        {"vietnamese": "Xe ôm", "english": "Motorbike taxi", "pronunciation": "se ohm", "accept": ["motorbike taxi", "bike taxi"]},
        {"vietnamese": "Máy bay", "english": "Airplane", "pronunciation": "mai bai", "accept": ["airplane", "plane", "flight"]},
        {"vietnamese": "Tàu / Xe lửa", "english": "Train", "pronunciation": "tau / se lua", "accept": ["train"]},
        {"vietnamese": "Thuyền", "english": "Boat", "pronunciation": "thwyen", "accept": ["boat", "ship"]},
    ],
    "body": [
        {"vietnamese": "Đầu", "english": "Head", "pronunciation": "dow", "accept": ["head"]},
        {"vietnamese": "Tóc", "english": "Hair", "pronunciation": "tok", "accept": ["hair"]},
        {"vietnamese": "Mặt", "english": "Face", "pronunciation": "mat", "accept": ["face"]},
        {"vietnamese": "Mắt", "english": "Eye(s)", "pronunciation": "mat", "accept": ["eye", "eyes"]},
        {"vietnamese": "Mũi", "english": "Nose", "pronunciation": "muy", "accept": ["nose"]},
        {"vietnamese": "Miệng", "english": "Mouth", "pronunciation": "myeng", "accept": ["mouth"]},
        {"vietnamese": "Tai", "english": "Ear(s)", "pronunciation": "tai", "accept": ["ear", "ears"]},
        {"vietnamese": "Răng", "english": "Tooth / teeth", "pronunciation": "rahng", "accept": ["tooth", "teeth"]},
        {"vietnamese": "Tay", "english": "Hand / arm", "pronunciation": "tai", "accept": ["hand", "arm"]},
        {"vietnamese": "Chân", "english": "Leg / foot", "pronunciation": "chun", "accept": ["leg", "foot", "feet"]},
        {"vietnamese": "Bụng", "english": "Stomach / belly", "pronunciation": "boong", "accept": ["stomach", "belly", "tummy"]},
        {"vietnamese": "Lưng", "english": "Back", "pronunciation": "luhng", "accept": ["back"]},
        {"vietnamese": "Tim", "english": "Heart", "pronunciation": "tim", "accept": ["heart"]},
    ],
    "emotions": [
        {"vietnamese": "Vui", "english": "Happy / glad", "pronunciation": "vwee", "accept": ["happy", "glad", "joyful"]},
        {"vietnamese": "Buồn", "english": "Sad", "pronunciation": "buohn", "accept": ["sad", "down"]},
        {"vietnamese": "Giận", "english": "Angry", "pronunciation": "yun", "accept": ["angry", "mad", "upset"]},
        {"vietnamese": "Sợ", "english": "Afraid / scared", "pronunciation": "shuh", "accept": ["afraid", "scared", "fear"]},
        {"vietnamese": "Mệt mỏi", "english": "Exhausted / worn out", "pronunciation": "met moy", "accept": ["exhausted", "worn out", "tired"]},
        {"vietnamese": "Lo lắng", "english": "Worried / anxious", "pronunciation": "lo lahng", "accept": ["worried", "anxious", "nervous"]},
        {"vietnamese": "Bận", "english": "Busy", "pronunciation": "bun", "accept": ["busy", "occupied"]},
        {"vietnamese": "Rảnh", "english": "Free / not busy", "pronunciation": "rahn", "accept": ["free", "not busy", "available"]},
        {"vietnamese": "Cô đơn", "english": "Lonely", "pronunciation": "koh duhn", "accept": ["lonely", "alone"]},
    ],
    "weather": [
        {"vietnamese": "Trời", "english": "Sky / weather", "pronunciation": "chuhy", "accept": ["sky", "weather"]},
        {"vietnamese": "Nắng", "english": "Sunny", "pronunciation": "nahng", "accept": ["sunny", "sun"]},
        {"vietnamese": "Mưa", "english": "Rain / raining", "pronunciation": "mua", "accept": ["rain", "raining"]},
        {"vietnamese": "Gió", "english": "Wind / windy", "pronunciation": "yo", "accept": ["wind", "windy"]},
        {"vietnamese": "Mây", "english": "Cloud / cloudy", "pronunciation": "may", "accept": ["cloud", "cloudy"]},
        {"vietnamese": "Bão", "english": "Storm / typhoon", "pronunciation": "bao", "accept": ["storm", "typhoon"]},
        {"vietnamese": "Sấm", "english": "Thunder", "pronunciation": "sum", "accept": ["thunder"]},
        {"vietnamese": "Mùa hè", "english": "Summer", "pronunciation": "mua he", "accept": ["summer"]},
        {"vietnamese": "Mùa đông", "english": "Winter", "pronunciation": "mua dohng", "accept": ["winter"]},
        {"vietnamese": "Mùa mưa", "english": "Rainy season", "pronunciation": "mua mua", "accept": ["rainy season", "wet season"]},
        {"vietnamese": "Mùa khô", "english": "Dry season", "pronunciation": "mua kho", "accept": ["dry season"]},
    ],
    "shopping": [
        {"vietnamese": "Tiền", "english": "Money", "pronunciation": "tee-en", "accept": ["money", "cash"]},
        {"vietnamese": "Tiền mặt", "english": "Cash", "pronunciation": "tee-en mat", "accept": ["cash"]},
        {"vietnamese": "Thẻ", "english": "Card (credit/debit)", "pronunciation": "the", "accept": ["card", "credit card", "debit card"]},
        {"vietnamese": "Đắt quá", "english": "Too expensive", "pronunciation": "dut kwa", "accept": ["too expensive", "too pricey"]},
        {"vietnamese": "Giảm giá", "english": "Discount / on sale", "pronunciation": "yam ya", "accept": ["discount", "sale", "on sale"]},
        {"vietnamese": "Cỡ", "english": "Size", "pronunciation": "kuh", "accept": ["size"]},
        {"vietnamese": "Thử", "english": "To try / try on", "pronunciation": "too", "accept": ["try", "try on"]},
        {"vietnamese": "Bớt chút được không?", "english": "Can you lower the price a bit?", "pronunciation": "buht chut duok khom", "accept": ["lower price", "cheaper", "discount it", "bargain"]},
        {"vietnamese": "Hóa đơn", "english": "Receipt / bill", "pronunciation": "hwa duhn", "accept": ["receipt", "bill", "invoice"]},
    ],
}


CATEGORY_ORDER = [
    "numbers", "addressing", "daily", "questions", "common_verbs", "adjectives",
    "ordering", "food", "shopping", "family", "emotions", "body",
    "colors", "time", "weather", "places", "transportation", "directions",
]
CATEGORY_LABELS = {
    "numbers": ("Numbers (0-1000)", "📚"),
    "addressing": ("Addressing People (by age)", "🙇"),
    "daily": ("Daily Phrases", "💬"),
    "questions": ("Question Words", "❓"),
    "common_verbs": ("Common Verbs", "🏃"),
    "adjectives": ("Adjectives", "🎨"),
    "ordering": ("Ordering & Restaurant", "🛍️"),
    "food": ("Food & Drinks", "🍜"),
    "shopping": ("Shopping & Money", "💰"),
    "family": ("Family", "👨‍👩‍👧"),
    "emotions": ("Emotions & Feelings", "😊"),
    "body": ("Body Parts", "🧍"),
    "colors": ("Colors", "🌈"),
    "time": ("Time & Days", "🗓️"),
    "weather": ("Weather & Seasons", "⛅"),
    "places": ("Everyday Places", "🏪"),
    "transportation": ("Transportation", "🚗"),
    "directions": ("Directions & Travel", "🧭"),
}


def normalize_answer(answer):
    """Normalize user answer for comparison"""
    return answer.strip().lower()


NUMBER_ALIASES = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
    "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten",
}


def _clean(text):
    """Lowercase, strip whitespace and trailing punctuation/ellipsis."""
    return normalize_answer(text).strip(".!?… ").replace("…", "").replace("'", "").replace(",", "")


def _acceptable_variants(word_item):
    """Build the set of accepted answers for a vocabulary entry.

    Includes the primary english answer, any '/'-separated alternatives within
    it, any explicit entries in the optional 'accept' list, and versions with
    parenthetical hints stripped out."""
    variants = set()

    def add(text):
        if not text:
            return
        variants.add(_clean(text))
        stripped = ""
        depth = 0
        for ch in text:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth = max(0, depth - 1)
            elif depth == 0:
                stripped += ch
        stripped = _clean(stripped)
        if stripped:
            variants.add(stripped)

    for part in word_item.get("english", "").split("/"):
        add(part.strip())
    for alt in word_item.get("accept", []) or []:
        add(alt)
    return {v for v in variants if v}


def _fuzzy_ratio(a, b):
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def check_answer(user_answer, word_item):
    """Return True if user's answer is close enough to any accepted variant.

    Combines exact match, number word/digit aliasing, and fuzzy similarity
    (SequenceMatcher >= 0.8) at both whole-string and per-word level."""
    user = _clean(user_answer)
    if not user:
        return False

    variants = _acceptable_variants(word_item)
    if user in variants:
        return True

    if user in NUMBER_ALIASES and NUMBER_ALIASES[user] in variants:
        return True

    for variant in variants:
        if _fuzzy_ratio(user, variant) >= SIMILARITY_THRESHOLD:
            return True
        v_words = variant.split()
        u_words = user.split()
        if len(v_words) >= 2 and u_words:
            matched = sum(
                1 for vw in v_words
                if any(_fuzzy_ratio(vw, uw) >= SIMILARITY_THRESHOLD for uw in u_words)
            )
            if matched / len(v_words) >= SIMILARITY_THRESHOLD:
                return True

    return False


# --- Progress tracking ---------------------------------------------------

def load_progress():
    """Load progress JSON, returning a default structure if missing/corrupt."""
    default = {"streak": 0, "last_played": None, "words": {}}
    if not os.path.exists(PROGRESS_FILE):
        return default
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in default:
            data.setdefault(key, default[key])
        return data
    except (json.JSONDecodeError, OSError):
        return default


def save_progress(progress):
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"  [Could not save progress: {e}]")


def update_streak(progress):
    """Update the daily streak based on today vs. last_played."""
    today = date.today().isoformat()
    last = progress.get("last_played")
    if last == today:
        return
    if last:
        last_d = datetime.fromisoformat(last).date()
        delta = (date.today() - last_d).days
        if delta == 1:
            progress["streak"] = progress.get("streak", 0) + 1
        elif delta > 1:
            progress["streak"] = 1
        else:
            progress["streak"] = max(1, progress.get("streak", 0))
    else:
        progress["streak"] = 1
    progress["last_played"] = today


def record_result(progress, word_item, correct):
    """Record seen/correct counts for a word."""
    key = word_item["vietnamese"]
    stats = progress["words"].setdefault(key, {"seen": 0, "correct": 0, "last_seen": None})
    stats["seen"] += 1
    if correct:
        stats["correct"] += 1
    stats["last_seen"] = date.today().isoformat()


def word_accuracy(progress, word_item):
    stats = progress["words"].get(word_item["vietnamese"])
    if not stats or stats["seen"] == 0:
        return None
    return stats["correct"] / stats["seen"]


# --- Quiz flow -----------------------------------------------------------

def run_quiz(words, progress, *, limit=None):
    """Run a quiz. If limit is given, only that many questions are asked."""
    if not words:
        print("No words in this set!")
        return

    shuffled = words.copy()
    random.shuffle(shuffled)
    if limit:
        shuffled = shuffled[:limit]

    score = 0
    questions_asked = 0
    total = len(shuffled)

    print(f"\nYou'll be asked {total} questions.")
    print("Commands: 'skip' | 'hint' (pronunciation) | 'say' (audio) | 'quit' / 'menu' (back to main menu)\n")

    for i, word_item in enumerate(shuffled, 1):
        vietnamese = word_item["vietnamese"]
        english = word_item["english"]
        pronunciation = word_item["pronunciation"]
        first_show = True

        while True:
            print(f"\n[Question {i}/{total}]")
            print(f"Vietnamese: {vietnamese}")
            if first_show:
                speak_vietnamese(vietnamese)
                first_show = False
            user_answer = input("English translation: ").strip()
            lowered = user_answer.lower()

            if lowered == "skip":
                print(f"✗ Skipped. Answer: {english}")
                questions_asked += 1
                record_result(progress, word_item, False)
                break
            if lowered == "hint":
                print(f"  Hint (pronunciation): {pronunciation}")
                continue
            if lowered == "say":
                print(f"  🔊 Playing: {vietnamese}")
                speak_vietnamese(vietnamese)
                continue
            if lowered in ("quit", "menu", "exit", "back"):
                print("  Ending quiz early — returning to menu...")
                total = questions_asked
                lowered = "quit"
                break
            if not user_answer:
                print("  Please enter an answer!")
                continue

            questions_asked += 1
            if check_answer(user_answer, word_item):
                print(f"✓ Correct! ({english})")
                score += 1
                record_result(progress, word_item, True)
            else:
                print(f"✗ Incorrect. Correct answer: {english}")
                accepted = sorted(_acceptable_variants(word_item))
                if len(accepted) > 1:
                    print(f"   (also accepts: {', '.join(a for a in accepted if a != english.lower())})")
                record_result(progress, word_item, False)
            break

        if lowered == "quit":
            break

    save_progress(progress)

    print("\n" + "=" * 50)
    print("QUIZ COMPLETE!")
    print("=" * 50)
    print(f"Score: {score}/{questions_asked}")
    pct = (score / questions_asked * 100) if questions_asked else 0
    print(f"Percentage: {pct:.1f}%")
    print(f"🔥 Daily streak: {progress['streak']} day(s)")

    if pct == 100:
        print("🎉 Perfect! You're a Vietnamese master!")
    elif pct >= 80:
        print("🌟 Great job! Keep it up!")
    elif pct >= 60:
        print("👍 Good progress! Review the ones you missed.")
    else:
        print("💪 Keep practicing! You'll get better!")
    print("=" * 50)


def all_words():
    out = []
    for key in CATEGORY_ORDER:
        out.extend(vocabulary.get(key, []))
    return out


def weak_words(progress, threshold=0.7):
    """Return words with accuracy below threshold, or never-seen-but-missed."""
    weak = []
    for word in all_words():
        acc = word_accuracy(progress, word)
        if acc is not None and acc < threshold:
            weak.append(word)
    return weak


def daily_practice_set(progress, size=15):
    """Mix weak words with a few new/less-seen ones for a daily session."""
    weak = weak_words(progress)
    seen_keys = set(progress["words"].keys())
    unseen = [w for w in all_words() if w["vietnamese"] not in seen_keys]
    random.shuffle(weak)
    random.shuffle(unseen)

    n_weak = min(len(weak), size // 2 if unseen else size)
    session = weak[:n_weak]
    remaining = size - len(session)
    session.extend(unseen[:remaining])

    if len(session) < size:
        pool = [w for w in all_words() if w not in session]
        random.shuffle(pool)
        session.extend(pool[: size - len(session)])

    random.shuffle(session)
    return session


def show_stats(progress):
    total_words = len(all_words())
    seen = len(progress["words"])
    total_seen = sum(s["seen"] for s in progress["words"].values())
    total_correct = sum(s["correct"] for s in progress["words"].values())
    overall_acc = (total_correct / total_seen * 100) if total_seen else 0

    print("\n" + "=" * 50)
    print("YOUR PROGRESS")
    print("=" * 50)
    print(f"🔥 Daily streak:     {progress.get('streak', 0)} day(s)")
    print(f"📅 Last played:      {progress.get('last_played') or 'never'}")
    print(f"📖 Words encountered: {seen}/{total_words}")
    print(f"🎯 Overall accuracy:  {overall_acc:.1f}% ({total_correct}/{total_seen})")

    weak = weak_words(progress)
    if weak:
        print(f"\n⚠️  Weak words ({len(weak)}):")
        for w in weak[:10]:
            acc = word_accuracy(progress, w)
            print(f"   - {w['vietnamese']:<25} {w['english']:<30} {acc*100:.0f}%")
        if len(weak) > 10:
            print(f"   ...and {len(weak) - 10} more")
    else:
        print("\n✨ No weak words — you're crushing it!")
    print("=" * 50)


def show_vocabulary_list(category_name, words):
    print(f"\n{'=' * 50}")
    print(f"{category_name.upper()}")
    print(f"{'=' * 50}\n")
    for word in words:
        print(f"Vietnamese:    {word['vietnamese']}")
        print(f"English:       {word['english']}")
        print(f"Pronunciation: {word['pronunciation']}")
        accept = word.get("accept") or []
        if accept:
            print(f"Also accepts:  {', '.join(accept)}")
        print("-" * 40)


def display_menu(progress):
    print("\n" + "=" * 50)
    print("VIETNAMESE LEARNING QUIZ")
    print("=" * 50)
    print(f"🔥 Streak: {progress.get('streak', 0)} day(s)   "
          f"📖 Words seen: {len(progress['words'])}/{len(all_words())}")
    print("-" * 50)
    print("  d. 🌅 Daily Practice (recommended)")
    print("  w. 🔁 Review Weak Words")
    print("  a. 🎯 Mix All Categories")
    print("  s. 📊 Show Stats")
    print("  v. 📘 Browse Vocabulary")
    print("  q. ❌ Quit")
    print()
    print("  Categories:")
    for i, key in enumerate(CATEGORY_ORDER, 1):
        label, emoji = CATEGORY_LABELS[key]
        print(f"   {i}. {emoji} {label}")
    print("-" * 50)


def browse_vocabulary():
    print("\nWhich category?")
    for i, key in enumerate(CATEGORY_ORDER, 1):
        label, emoji = CATEGORY_LABELS[key]
        print(f"  {i}. {emoji} {label}")
    choice = input("Enter number (or Enter to cancel): ").strip()
    if not choice.isdigit():
        return
    idx = int(choice) - 1
    if 0 <= idx < len(CATEGORY_ORDER):
        key = CATEGORY_ORDER[idx]
        label, _ = CATEGORY_LABELS[key]
        show_vocabulary_list(label, vocabulary[key])


def main():
    print("\n" + "=" * 50)
    print("Welcome to Vietnamese Learning Quiz!")
    print("=" * 50)

    progress = load_progress()
    update_streak(progress)
    save_progress(progress)

    while True:
        display_menu(progress)
        choice = input("Your choice: ").strip().lower()

        if choice == "q":
            print("\nTạm biệt! Keep practicing! 👋")
            break
        if choice == "s":
            show_stats(progress)
            continue
        if choice == "v":
            browse_vocabulary()
            continue
        if choice == "d":
            print("\n🌅 Daily Practice")
            run_quiz(daily_practice_set(progress, size=15), progress)
            continue
        if choice == "w":
            weak = weak_words(progress)
            if not weak:
                print("\n✨ No weak words to review — try Daily Practice!")
                continue
            print(f"\n🔁 Reviewing {len(weak)} weak words")
            run_quiz(weak, progress)
            continue
        if choice == "a":
            print("\n🎯 Mixed Quiz (All Categories)")
            run_quiz(all_words(), progress, limit=25)
            continue
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(CATEGORY_ORDER):
                key = CATEGORY_ORDER[idx]
                label, emoji = CATEGORY_LABELS[key]
                print(f"\n{emoji} {label}")
                run_quiz(vocabulary[key], progress)
                continue

        print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
