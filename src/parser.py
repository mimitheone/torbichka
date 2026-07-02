"""HTML parser module for extracting product data from Kaufland Bulgaria website."""

import json
import re
import logging
from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
from decimal import Decimal, InvalidOperation


class KauflandParser:
    """Parser class for Kaufland Bulgaria product pages."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._offer_id_by_image_slug: Dict[str, str] = {}
        self._ssr_offers_by_slug: Dict[str, List[Dict[str, Any]]] = {}
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def _extract_manufacturer_from_name(self, name: str) -> Optional[str]:
        """Extract manufacturer from product name using common patterns."""
        if not name:
            return None
        
        name_lower = name.lower()
        name_lower_clean = re.sub(r'[^\w\s]', ' ', name_lower).strip()
        
        # Pattern 1: Manufacturer with slash (MILKA/ OREO → MILKA) - CHECK FIRST
        # This should be checked before all-caps pattern to properly split on "/"
        slash_match = re.search(r'^([A-Z][A-Z\s&]+?)\s*/\s*', name)
        if slash_match:
            manufacturer = slash_match.group(1).strip()
            if len(manufacturer.split()) <= 2 and manufacturer.replace(' ', '').isupper():
                return manufacturer
        
        # Pattern 2: All caps manufacturer at start (MILKA, OREO, etc.)
        # This has priority because "MILKA" should be extracted as "MILKA", not "Milka"
        caps_match = re.search(r'^([A-Z][A-Z\s&]+?)(?:\s+[a-zА-Я]|\s*$)', name)
        if caps_match:
            manufacturer = caps_match.group(1).strip()
            # Don't include trailing slash in the result
            manufacturer = manufacturer.rstrip('/').strip()
            if len(manufacturer.split()) <= 3 and manufacturer.replace(' ', '').isupper():
                return manufacturer
        
        # Known manufacturers list (expandable) - checked after all-caps patterns
        known_manufacturers_map = {
            'milka': 'Milka',
            'oreo': 'Oreo',
            'nestle': 'Nestle',
            'danone': 'Danone',
            'activia': 'Activia',
            'славянка': 'Славянка',
            'бачо киро': 'Бачо Киро',
            'добруджа': 'Добруджа',
            'стария ловец': 'Стария ловец',  # Preserve original case
            'joli': 'Joli',
            'laica': 'Laica',
            'орехите': 'Орехите',
            'деком': 'Деком',
            'oyanda': 'Oyanda',
            'townland': 'Townland'
        }
        
        # Check if name starts with known manufacturer (whole word match)
        for manufacturer_lower, manufacturer_canonical in known_manufacturers_map.items():
            if name_lower_clean.startswith(manufacturer_lower):
                if name_lower_clean == manufacturer_lower or name_lower_clean.startswith(manufacturer_lower + ' '):
                    # Try to preserve original case from the name
                    if manufacturer_lower in name_lower:
                        # Find the original case in the name
                        start_idx = name_lower.find(manufacturer_lower)
                        original = name[start_idx:start_idx+len(manufacturer_lower)]
                        # If original matches the canonical form or is all lowercase, use canonical
                        if original == manufacturer_canonical or original.lower() == manufacturer_lower:
                            return manufacturer_canonical
                        else:
                            return original.title() if original.islower() else original
                    return manufacturer_canonical
        
        # Pattern 3: Single word that looks like a brand (Joli, Laica, etc.)
        words = name.split()
        if len(words) == 1:
            if name[0].isupper() and len(name) <= 15:
                skip_single = ['after', 'before', 'fresh', 'new', 'old', 'best', 'extra',
                              'super', 'ultra', 'premium', 'deluxe', 'classic']
                if name_lower not in skip_single:
                    return name
        
        # Pattern 4: First word that looks like a brand
        skip_words = ['after', 'before', 'fresh', 'new', 'old', 'best', 'extra',
                     'super', 'ultra', 'premium', 'deluxe', 'classic', 'български',
                     'бяло', 'праз', 'тиква', 'земел', 'многозърнест', 'ръчна',
                     'сгъваема', 'филтър', 'или']
        
        first_word_match = re.search(r'^([A-ZА-Я][a-zа-я]+)(?:\s|$|/)', name)
        if first_word_match:
            first_word = first_word_match.group(1)
            if first_word.lower() not in skip_words:
                rest = name[len(first_word):].strip()
                if not rest or rest[0] in ['-', '/'] or (rest and rest[0].isupper()):
                    return first_word
        
        return None
    
    def _extract_origin_from_product(self, product_element, subtitle: Optional[str] = None, name: Optional[str] = None) -> Optional[str]:
        """Extract origin/country information from product element."""
        # Pattern 1: Regionality logo - BG.png = България
        regionality_logo = product_element.select_one('.k-product-tile__regionality-logo')
        if regionality_logo:
            src = regionality_logo.get('src', '')
            if 'BG.png' in src:
                return 'България'
            # Can add more country mappings if needed
            country_match = re.search(r'/([A-Z]{2})\.png', src)
            if country_match:
                country_code = country_match.group(1)
                country_map = {
                    'BG': 'България',
                    'DE': 'Германия',
                    'IT': 'Италия',
                    'GR': 'Гърция',
                    'RO': 'Румъния',
                    'TR': 'Турция',
                    'ES': 'Испания',
                    'FR': 'Франция'
                }
                if country_code in country_map:
                    return country_map[country_code]
        
        # Pattern 2: Check subtitle and description for origin indicators
        origin_keywords = {
            'от кюспе': 'от кюспе',
            'от свежата витрина': 'от свежата витрина',
            'българия': 'България',
            'български': 'България',
            'българско': 'България'
        }
        
        text_to_check = []
        if subtitle:
            text_to_check.append(subtitle.lower())
        if name:
            text_to_check.append(name.lower())
        
        for text in text_to_check:
            for keyword, origin_value in origin_keywords.items():
                if keyword in text:
                    return origin_value
        
        # Pattern 3: Check image alt/title for origin info
        img_element = product_element.select_one('img')
        if img_element:
            for attr in ['alt', 'title']:
                img_text = img_element.get(attr, '').lower()
                if img_text:
                    for keyword, origin_value in origin_keywords.items():
                        if keyword in img_text:
                            return origin_value
        
        return None
    
    def _extract_grade_from_product(self, product_element, subtitle: Optional[str] = None, name: Optional[str] = None) -> Optional[str]:
        """Extract grade/variety information from product element."""
        # Pattern 1: Check subtitle for grade/variety indicators
        grade_patterns = [
            r'(различни сортове)',
            r'(различни видове)',
            r'(различни вкусове)',
            r'(сорт\s+[А-Яа-я]+)',
            r'([А-Яа-я]+\s+сорт)',
        ]
        
        text_to_check = []
        if subtitle:
            text_to_check.append(subtitle)
        if name:
            text_to_check.append(name)
        
        for text in text_to_check:
            if not text:
                continue
            for pattern in grade_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    grade_text = match.group(1) if match.groups() else match.group(0)
                    return self._clean_text(grade_text)
        
        # Pattern 2: Extract specific grade names from subtitle
        # Common patterns: "Филе Трапезица", "Луканка Смядовска", "Кашкавал от краве мляко"
        if subtitle:
            # Look for region-specific names that indicate grade
            grade_indicators = [
                r'([А-Яа-я]+\s+[А-Яа-я]+)\s+(?:от|с)',  # "Филе Трапезица от"
                r'([А-Яа-я]+\s+[А-Яа-я]+)\s+различни',  # "Сирене Бяло различни"
            ]
            for pattern in grade_indicators:
                match = re.search(pattern, subtitle, re.IGNORECASE)
                if match:
                    grade = match.group(1)
                    # Don't treat common words as grades
                    skip_words = ['от', 'с', 'различни', 'или', 'и']
                    if grade.lower() not in skip_words and len(grade) > 3:
                        return grade.strip()
        
        # Pattern 3: Check if subtitle contains a variety name (often after manufacturer)
        if subtitle:
            # Split subtitle and look for variety names
            parts = subtitle.split()
            if len(parts) >= 2:
                # Often format: "Manufacturer Variety Description"
                # Take the second part if it looks like a variety name
                potential_grade = parts[1] if len(parts) > 1 else None
                if potential_grade and len(potential_grade) > 3 and potential_grade[0].isupper():
                    skip_words = ['от', 'с', 'различни', 'или', 'и', 'видове', 'вкусове', 'сортове']
                    if potential_grade.lower() not in skip_words:
                        return potential_grade
        
        return None
    
    def _extract_weight_from_name(self, name: str) -> Optional[str]:
        """Extract weight/quantity from product name."""
        if not name:
            return None
        
        # Weight patterns
        weight_patterns = [
            r'(\d+[.,]?\d*\s*кг)',      # kg
            r'(\d+[.,]?\d*\s*г)',       # grams
            r'(\d+[.,]?\d*\s*л)',       # liters
            r'(\d+[.,]?\d*\s*мл)',      # ml
            r'(\d+\s*х\s*\d+[.,]?\d*\s*г)',  # multiple items
            r'(\d+\s*бр\.?)',           # pieces
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_discount_info(self, product_element) -> Optional[Dict[str, Any]]:
        """Extract discount information."""
        discount_selectors = [
            '.discount',
            '.sale',
            '.promo',
            '.offer',
            '.price-reduction',
            '.special-price'
        ]
        
        for selector in discount_selectors:
            discount_element = product_element.select_one(selector)
            if discount_element:
                discount_text = self._clean_text(discount_element.get_text())
                if discount_text:
                    # Extract percentage or amount
                    percent_match = re.search(r'(\d+)\s*%', discount_text)
                    amount_match = re.search(r'(\d+[.,]?\d*)\s*(лв|BGN)', discount_text)
                    
                    return {
                        'text': discount_text,
                        'percentage': percent_match.group(1) if percent_match else None,
                        'amount': amount_match.group(1) if amount_match else None
                    }
        
        return None
    
    def _extract_availability(self, product_element) -> str:
        """Extract availability status."""
        availability_selectors = [
            '.availability',
            '.stock',
            '.in-stock',
            '.out-of-stock'
        ]
        
        for selector in availability_selectors:
            availability_element = product_element.select_one(selector)
            if availability_element:
                availability_text = self._clean_text(availability_element.get_text()).lower()
                if 'налич' in availability_text or 'stock' in availability_text:
                    return 'Налично'
                elif 'изчерп' in availability_text or 'out' in availability_text:
                    return 'Неналично'

        return ''
    
    def _extract_image_id_from_url(self, url: str) -> Optional[str]:
        """Извлича уникалния image ID от Kaufland URL на снимката.
        Пример: https://kaufland.media.schwarz/is/image/schwarz/01004080_P -> 01004080_P
        """
        if not url or 'kaufland.media.schwarz' not in url:
            return None
        match = re.search(r'/schwarz/([^/?#]+)', url)
        return match.group(1) if match else None

    def _build_offer_id_by_image_slug(self, html_content: str) -> Dict[str, str]:
        """От SSR JSON: listImage slug -> offerId (първи срещнат при дубликати на снимка)."""
        ids = re.findall(r'"offerId":"([^"]+)"', html_content)
        imgs = re.findall(r'"listImage":"(https://[^"]+)"', html_content)
        out: Dict[str, str] = {}
        if len(ids) != len(imgs):
            self.logger.warning(
                "offerId/listImage брой в JSON не съвпада (%s vs %s)",
                len(ids),
                len(imgs),
            )
        for oid, img in zip(ids, imgs):
            slug = img.rstrip('/').split('/')[-1].split('?')[0]
            if slug and slug not in out:
                out[slug] = oid
        return out

    def _kaufland_offer_page_url(self, offer_id: str) -> str:
        """Deep link към офертната страница (SPA); offer_id от JSON."""
        from urllib.parse import quote

        q = quote(offer_id, safe='')
        return (
            'https://www.kaufland.bg/aktualni-predlozheniya/oferti.html'
            f'?kloffer-week=current&kloffer-offer={q}'
        )

    def _parse_ssr_offer_template_offers(self, html_content: str) -> List[Dict[str, Any]]:
        """Всички оферти от window.SSR OfferTemplate (offerId, klNr, listImage, title, …)."""
        offers: List[Dict[str, Any]] = []
        for m in re.finditer(r"window\.SSR\['[0-9a-f-]+'\]\s*=\s*(\{)", html_content):
            start = m.end(1) - 1
            depth = 0
            for i in range(start, len(html_content)):
                c = html_content[i]
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        chunk = html_content[start : i + 1]
                        try:
                            data = json.loads(chunk)
                        except json.JSONDecodeError:
                            break
                        if data.get("component") != "OfferTemplate":
                            break
                        props = data.get("props") or {}
                        od = props.get("offerData") or {}
                        for cy in od.get("cycles", []):
                            for cat in cy.get("categories", []):
                                for of in cat.get("offers", []):
                                    url = of.get("listImage") or ""
                                    slug = url.rstrip("/").split("/")[-1].split("?")[0]
                                    if not slug:
                                        continue
                                    row = dict(of)
                                    row["image_slug"] = slug
                                    offers.append(row)
                        return offers
        return offers

    def _norm_tokens(self, text: str) -> set:
        if not text:
            return set()
        return set(re.findall(r"[\w\u0400-\u04FF]+", text.lower()))

    def _offer_match_score(
        self, tile_title: str, tile_subtitle: str, offer: Dict[str, Any]
    ) -> float:
        """Колко добре плочката съвпада с офертата от SSR (0..1+)."""
        parts_o = [
            offer.get("title") or "",
            offer.get("subtitle") or "",
            offer.get("detailTitle") or "",
            offer.get("detailDescription") or "",
        ]
        blob_o = self._clean_text(" ".join(parts_o)).lower()
        blob_t = self._clean_text(f"{tile_title or ''} {tile_subtitle or ''}").lower()
        if not blob_t:
            return 0.0
        tt = self._norm_tokens(tile_title)
        ts = self._norm_tokens(tile_subtitle)
        tile_tokens = tt | ts
        if not tile_tokens:
            return 0.0
        offer_tokens = self._norm_tokens(blob_o)
        inter = tile_tokens & offer_tokens
        jacc = len(inter) / max(1, len(tile_tokens | offer_tokens))
        # директно съвпадение на заглавието с title или detailTitle
        nt = self._clean_text(tile_title).lower()
        bonus = 0.0
        if nt and nt == self._clean_text(offer.get("title") or "").lower():
            bonus += 0.35
        if nt and nt == self._clean_text(offer.get("detailTitle") or "").lower():
            bonus += 0.35
        if blob_t.replace(" ", "") and blob_t.replace(" ", "") in blob_o.replace(" ", ""):
            bonus += 0.25
        return min(1.5, jacc + bonus)

    def _pick_best_ssr_offer(
        self, candidates: List[Dict[str, Any]], tile_title: str, tile_subtitle: str
    ) -> Optional[Dict[str, Any]]:
        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]
        best: Optional[Tuple[float, Dict[str, Any]]] = None
        for off in candidates:
            sc = self._offer_match_score(tile_title, tile_subtitle or "", off)
            if best is None or sc > best[0]:
                best = (sc, off)
        if best and best[0] >= 0.12:
            return best[1]
        return candidates[0]

    def _assign_product_ids_from_ssr(
        self,
        product_data: Dict[str, Any],
        image_slug: Optional[str],
        tile_title: str,
        tile_subtitle: Optional[str],
    ) -> None:
        """Попълва kl_nr, offer_id, product_id = kaufland_bg:klNr:image_slug."""
        matched: Optional[Dict[str, Any]] = None
        if image_slug and self._ssr_offers_by_slug:
            cands = self._ssr_offers_by_slug.get(image_slug, [])
            if len(cands) == 1:
                matched = cands[0]
            elif len(cands) > 1:
                matched = self._pick_best_ssr_offer(cands, tile_title, tile_subtitle or "")
        kl = ""
        oid = None
        if matched:
            kl = str(matched.get("klNr") or "").strip()
            oid = matched.get("offerId")
        product_data["kl_nr"] = kl
        product_data["offer_id"] = oid
        if image_slug:
            if kl:
                product_data["product_id"] = f"kaufland_bg:{kl}:{image_slug}"
            else:
                product_data["product_id"] = f"kaufland_bg::__:{image_slug}"
        else:
            product_data["product_id"] = ""

    def _extract_price(self, price_text: str) -> Optional[Dict[str, Any]]:
        """Extract and parse price information."""
        if not price_text:
            return None
        
        # Remove common currency symbols and clean text
        clean_price = re.sub(r'[^\d.,лв\s]', '', price_text)
        
        # Extract numeric price
        price_match = re.search(r'(\d+[.,]?\d*)', clean_price)
        if not price_match:
            return None
        
        try:
            price_str = price_match.group(1).replace(',', '.')
            price_value = float(price_str)
            
            # Цените в България вече са в евро (Kaufland BG)
            currency = "EUR"
            if "лв" in clean_price or "BGN" in price_text:
                currency = "BGN"
            elif "€" in price_text or "EUR" in price_text:
                currency = "EUR"
            elif "$" in price_text or "USD" in price_text:
                currency = "USD"
            
            return {
                "value": price_value,
                "currency": currency,
                "original_text": price_text.strip()
            }
        
        except (ValueError, InvalidOperation):
            self.logger.warning(f"Could not parse price: {price_text}")
            return None
    
    def _extract_product_info(self, product_element) -> Optional[Dict[str, Any]]:
        """Extract information from a single product element."""
        try:
            product_data = {
                # Initialize all required fields
                'name': None,                    # Име
                'manufacturer': None,            # Производител  
                'weight_unit': None,             # Грамаж/бройка
                'category': None,                # тип/вид/под категория
                'origin': None,                  # Произход
                'grade': None,                   # Сорт
                'price': None,                   # Цена(евро/БГН)
                'discount': None,                # Отстъпка
                'description': None,             # Описание
                'availability': None,            # Налично/неналично
                'price_currency': 'EUR',        # Kaufland BG – цени в евро
                'image_url': None,
                'image_id': None,               # slug от listImage URL (не е глобално уникален)
                'kl_nr': None,                  # Kaufland klNr от SSR
                'offer_id': None,               # offerId от SSR
                'product_id': None,             # kaufland_bg:klNr:slug — ключ за база/CSV
                'product_url': None,
                'scraped_at': None,
                'source': 'kaufland.bg'
            }
            
            # Try multiple possible selectors for product name (Kaufland specific)
            name_selectors = [
                '.k-product-tile__title',
                '.k-product-tile__name',
                '.product-name',
                '.product-title', 
                'h2',
                'h3',
                '.title',
                '[data-testid="product-name"]',
                '.product-card-title',
                '.item-title',
                '.product-info h3',
                '.product-info h2'
            ]
            
            name = None
            for selector in name_selectors:
                name_element = product_element.select_one(selector)
                if name_element:
                    name = self._clean_text(name_element.get_text())
                    if name:
                        break
            
            if not name:
                # Fallback: try to find any text that looks like a product name
                text_elements = product_element.find_all(text=True)
                for text in text_elements:
                    clean_text = self._clean_text(text)
                    if len(clean_text) > 10 and not re.match(r'^\d+[.,]?\d*', clean_text):
                        name = clean_text
                        break
            
            if not name:
                return None
            
            product_data['name'] = name
            
            # Extract subtitle (additional product description)
            subtitle_element = product_element.select_one('.k-product-tile__subtitle')
            subtitle = None
            if subtitle_element:
                subtitle = self._clean_text(subtitle_element.get_text())
                # If subtitle exists, combine with name for full description
                if subtitle and subtitle not in name:
                    product_data['description'] = f"{name} - {subtitle}"
                    # Also try to extract more info from subtitle
                    if not product_data.get('category'):
                        product_data['category'] = subtitle
            
            # Try to extract from image alt/title attributes (they often have full descriptions)
            img_element = product_element.select_one('.k-product-tile__main-image, img.k-product-tile__main-image')
            if img_element:
                img_alt = img_element.get('alt', '') or ''
                img_title = img_element.get('title', '') or ''
                
                # Extract from alt/title - they often have "Изображение на [Full Product Name]"
                for img_text in [img_alt, img_title]:
                    if img_text and 'Изображение на' in img_text:
                        full_desc = img_text.replace('Изображение на', '').strip()
                        if full_desc and len(full_desc) > len(name):
                            if not product_data.get('description'):
                                product_data['description'] = full_desc
                            # Try to extract category from full description
                            if 'от нашата пекарна' in full_desc.lower():
                                product_data['category'] = 'Пекарна'
            
            # Extract manufacturer from product name (common patterns)
            manufacturer = self._extract_manufacturer_from_name(name)
            if manufacturer:
                product_data['manufacturer'] = manufacturer
            
            # Extract weight/quantity from product name or subtitle
            weight_unit = self._extract_weight_from_name(name)
            if not weight_unit and subtitle:
                weight_unit = self._extract_weight_from_name(subtitle)
            if weight_unit:
                product_data['weight_unit'] = weight_unit
            
            # Extract availability
            product_data['availability'] = self._extract_availability(product_element)
            
            # Extract origin from product element
            origin = self._extract_origin_from_product(product_element, subtitle, name)
            if origin:
                product_data['origin'] = origin
            
            # Extract grade from product element
            grade = self._extract_grade_from_product(product_element, subtitle, name)
            if grade:
                product_data['grade'] = grade
            
            # Extract discount information (Kaufland specific)
            discount_element = product_element.select_one('.k-price-tag__discount')
            if discount_element:
                discount_text = self._clean_text(discount_element.get_text())
                product_data['discount'] = {'text': discount_text}
            else:
                discount_info = self._extract_discount_info(product_element)
                if discount_info:
                    product_data['discount'] = discount_info
            
            # Extract old price for Kaufland
            old_price_element = product_element.select_one('.k-price-tag__old-price')
            if old_price_element:
                old_price_text = self._clean_text(old_price_element.get_text())
                old_price_parsed = self._extract_price(old_price_text)
                if old_price_parsed:
                    if not product_data.get('discount'):
                        product_data['discount'] = {}
                    product_data['discount']['old_price'] = old_price_parsed
            
            # Extract unit price (Kaufland: грамаж)
            unit_price_element = product_element.select_one('.k-product-tile__unit-price')
            if unit_price_element:
                unit_price_text = self._clean_text(unit_price_element.get_text())
                if unit_price_text:
                    product_data['weight_unit'] = unit_price_text
            
            # Extract base price (цена на кг)
            base_price_element = product_element.select_one('.k-product-tile__base-price')
            if base_price_element:
                base_price_text = self._clean_text(base_price_element.get_text())
                # Extract price per kg from text like "(1 кг = 12,53 ЛВ.)"
                base_price_match = re.search(r'=\s*(\d+[.,]\d+)', base_price_text)
                if base_price_match:
                    try:
                        product_data['price_per_kg'] = float(base_price_match.group(1).replace(',', '.'))
                    except ValueError:
                        pass
            
            # Try multiple possible selectors for price (Kaufland specific)
            price_selectors = [
                '.k-price-tag__price',
                '.k-product-tile__price',
                '.price',
                '.product-price',
                '.current-price',
                '.price-current',
                '[data-testid="price"]',
                '.price-value',
                '.product-card-price'
            ]
            
            price_info = None
            for selector in price_selectors:
                price_element = product_element.select_one(selector)
                if price_element:
                    price_text = self._clean_text(price_element.get_text())
                    price_info = self._extract_price(price_text)
                    if price_info:
                        break
            
            if not price_info:
                # Fallback: look for any text that contains price patterns
                text_elements = product_element.find_all(text=True)
                for text in text_elements:
                    if re.search(r'\d+[.,]?\d*\s*(лв|BGN|€|EUR|\$|USD)', text):
                        price_info = self._extract_price(text)
                        if price_info:
                            break
            
            # Enhanced price processing
            if price_info:
                product_data['price'] = price_info
                product_data['price_currency'] = price_info.get('currency', 'EUR')

            # Try to extract additional information
            # Product image (already extracted above, but make sure we have the URL)
            if not product_data.get('image_url'):
                img_element = product_element.select_one('img')
                if img_element:
                    img_src = img_element.get('src') or img_element.get('data-src')
                    if img_src:
                        product_data['image_url'] = img_src
            # Уникален image_id от Kaufland URL: https://kaufland.media.schwarz/is/image/schwarz/01004080_P
            if product_data.get('image_url'):
                product_data['image_id'] = self._extract_image_id_from_url(product_data['image_url'])
            
            # Product link (реален href; на офертни страници често е # — тогава SSR по image_id)
            link_root = product_element if getattr(product_element, 'name', '') == 'a' else None
            link_element = link_root or product_element.select_one('a.k-product-tile') or product_element.select_one('a')
            if link_element:
                href = link_element.get('href')
                if href and not href.startswith('#'):
                    if href.startswith('/'):
                        href = 'https://www.kaufland.bg' + href
                    product_data['product_url'] = href
            slug = product_data.get('image_id')
            self._assign_product_ids_from_ssr(
                product_data, slug, product_data.get('name') or '', subtitle
            )

            if not product_data.get('product_url') and product_data.get('offer_id'):
                product_data['product_url'] = self._kaufland_offer_page_url(
                    str(product_data['offer_id'])
                )
            elif not product_data.get('product_url') and self._offer_id_by_image_slug:
                iid = product_data.get('image_id')
                if iid:
                    oid = self._offer_id_by_image_slug.get(iid)
                    if oid:
                        product_data['product_url'] = self._kaufland_offer_page_url(oid)

            # Product description or additional details
            desc_selectors = [
                '.product-description',
                '.product-details',
                '.description',
                '.product-info'
            ]
            
            for selector in desc_selectors:
                desc_element = product_element.select_one(selector)
                if desc_element:
                    desc_text = self._clean_text(desc_element.get_text())
                    if desc_text and len(desc_text) > 5:
                        product_data['description'] = desc_text
                        break
            
            # Add metadata
            product_data['scraped_at'] = None  # Will be set by the main script
            product_data['source'] = 'kaufland.bg'
            
            return product_data
            
        except Exception as e:
            self.logger.error(f"Error extracting product info: {e}")
            return None
    
    def parse_products(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse HTML content and extract all products."""
        if not html_content:
            self.logger.error("No HTML content provided")
            return []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            self._offer_id_by_image_slug = self._build_offer_id_by_image_slug(html_content)

            ssr_offers = self._parse_ssr_offer_template_offers(html_content)
            self._ssr_offers_by_slug = defaultdict(list)
            for o in ssr_offers:
                self._ssr_offers_by_slug[o["image_slug"]].append(o)
            if ssr_offers:
                self.logger.info(
                    "SSR OfferTemplate: %s оферти, %s различни image_slug",
                    len(ssr_offers),
                    len(self._ssr_offers_by_slug),
                )

            products = []
            
            # Try multiple possible selectors for product containers (Kaufland specific first)
            product_selectors = [
                '.k-product-tile',
                'a.k-product-tile',
                '.product',
                '.product-item',
                '.product-card',
                '.product-container',
                '[data-testid="product"]',
                '.product-tile',
                '.item',
                '.product-list-item'
            ]
            
            product_elements = []
            for selector in product_selectors:
                elements = soup.select(selector)
                if elements:
                    product_elements = elements
                    self.logger.info(f"Found {len(elements)} products using selector: {selector}")
                    break
            
            if not product_elements:
                # Fallback: look for common patterns in the HTML
                self.logger.warning("No products found with standard selectors, trying fallback methods")
                
                # Look for divs that might contain product information
                potential_products = soup.find_all('div', class_=re.compile(r'product|item|card'))
                if potential_products:
                    product_elements = potential_products
                    self.logger.info(f"Found {len(potential_products)} potential products using fallback")
            
            if not product_elements:
                self.logger.error("No product elements found in the page")
                return []
            
            for element in product_elements:
                product_data = self._extract_product_info(element)
                if product_data and product_data.get('name'):
                    products.append(product_data)
            
            self.logger.info(f"Successfully parsed {len(products)} products")
            return products

        except Exception as e:
            self.logger.error(f"Error parsing HTML content: {e}")
            return []
        finally:
            self._offer_id_by_image_slug = {}
            self._ssr_offers_by_slug = {}
    
    def validate_product_data(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and clean product data."""
        valid_products = []
        
        for product in products:
            # Check if product has minimum required fields - name AND at least one of price/weight
            if not product.get('name'):
                continue
            
            # Clean product name
            product['name'] = self._clean_text(product['name'])
            
            # Filter out navigation/UI elements - must have either price or weight_unit
            has_price = product.get('price') and isinstance(product.get('price'), dict)
            has_weight = product.get('weight_unit')
            
            if not has_price and not has_weight:
                self.logger.debug(f"Skipping non-product element: {product['name']}")
                continue
            
            # Filter out common non-product names
            non_product_keywords = [
                'accordion', 'slider', 'button', 'navigation', 'menu',
                'header', 'footer', 'banner', 'sidebar', 'link',
                'всички оферти', 'виж още', 'регистрир', 'търсене',
                'списък', 'профил', 'филиал', 'това не е'
            ]
            
            name_lower = product['name'].lower()
            if any(keyword in name_lower for keyword in non_product_keywords):
                self.logger.debug(f"Filtering out UI element: {product['name']}")
                continue
            
            # Filter out very short names (likely UI elements)
            if len(product['name']) < 3:
                continue
            
            # Validate price
            if product.get('price') and isinstance(product['price'], dict):
                price_value = product['price'].get('value')
                if not isinstance(price_value, (int, float)) or price_value <= 0:
                    product['price'] = None
            
            valid_products.append(product)
        
        self.logger.info(f"Validated {len(valid_products)} out of {len(products)} products")
        return valid_products
    
    def extract_detailed_product_info(self, product_html: str, base_product: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed information from individual product page HTML."""
        if not product_html or not base_product:
            return base_product
        
        try:
            soup = BeautifulSoup(product_html, 'html.parser')
            detailed_product = base_product.copy()
            
            # Extract category/subcategory information
            category = self._extract_category_from_page(soup)
            if category:
                detailed_product['category'] = category
            
            # Extract origin/country information
            origin = self._extract_origin_from_page(soup)
            if origin:
                detailed_product['origin'] = origin
            
            # Extract grade/quality information
            grade = self._extract_grade_from_page(soup)
            if grade:
                detailed_product['grade'] = grade
            
            # Extract detailed description
            description = self._extract_detailed_description(soup)
            if description:
                detailed_product['description'] = description
            
            # Extract promotion and discount information
            promotion_info = self._extract_promotion_info(soup)
            if promotion_info:
                detailed_product.update(promotion_info)
            
            # Extract more detailed availability information
            detailed_availability = self._extract_detailed_availability(soup)
            if detailed_availability:
                detailed_product['availability'] = detailed_availability
            
            return detailed_product
            
        except Exception as e:
            self.logger.error(f"Error extracting detailed product info: {e}")
            return base_product
    
    def _extract_category_from_page(self, soup) -> Optional[str]:
        """Extract category/subcategory from product page."""
        category_selectors = [
            '.breadcrumb',
            '.breadcrumbs',
            '.category-path',
            '.product-category',
            'nav[aria-label="breadcrumb"]',
            '.navigation-path'
        ]
        
        for selector in category_selectors:
            breadcrumb = soup.select_one(selector)
            if breadcrumb:
                # Extract category path from breadcrumb
                links = breadcrumb.find_all('a')
                if len(links) >= 2:  # Skip "Home" and get actual categories
                    categories = [self._clean_text(link.get_text()) for link in links[1:]]
                    return ' > '.join(categories) if categories else None
                
                # Fallback: get all text from breadcrumb
                breadcrumb_text = self._clean_text(breadcrumb.get_text())
                if breadcrumb_text and len(breadcrumb_text) > 5:
                    return breadcrumb_text
        
        return None
    
    def _extract_origin_from_page(self, soup) -> Optional[str]:
        """Extract origin/country information from product page."""
        origin_patterns = [
            r'произход[:\s]*([^,\n]+)',
            r'origin[:\s]*([^,\n]+)',
            r'страна[:\s]*([^,\n]+)',
            r'country[:\s]*([^,\n]+)',
        ]
        
        # Look in product details, specifications, or description sections
        detail_sections = soup.find_all(['div', 'section', 'table'], 
                                      class_=re.compile(r'(detail|spec|info|description)', re.I))
        
        for section in detail_sections:
            section_text = section.get_text().lower()
            for pattern in origin_patterns:
                match = re.search(pattern, section_text, re.IGNORECASE)
                if match:
                    origin = self._clean_text(match.group(1))
                    # Clean up common suffixes and extra text
                    origin = re.sub(r'хората.*$', '', origin, flags=re.IGNORECASE)
                    origin = re.sub(r'\s+', ' ', origin).strip()
                    if len(origin) > 2 and len(origin) < 50:  # Reasonable length
                        return origin.title()
        
        return None
    
    def _extract_grade_from_page(self, soup) -> Optional[str]:
        """Extract grade/quality information from product page."""
        grade_patterns = [
            r'сорт[:\s]*([^,\n]+)',
            r'качество[:\s]*([^,\n]+)',
            r'клас[:\s]*([^,\n]+)',
            r'grade[:\s]*([^,\n]+)',
            r'quality[:\s]*([^,\n]+)',
        ]
        
        # Look in product details or specifications
        detail_sections = soup.find_all(['div', 'section', 'table'], 
                                      class_=re.compile(r'(detail|spec|info)', re.I))
        
        for section in detail_sections:
            section_text = section.get_text().lower()
            for pattern in grade_patterns:
                match = re.search(pattern, section_text, re.IGNORECASE)
                if match:
                    grade = self._clean_text(match.group(1))
                    if len(grade) > 1:
                        return grade.title()
        
        return None
    
    def _extract_detailed_description(self, soup) -> Optional[str]:
        """Extract detailed product description from product page."""
        description_selectors = [
            '.product-description',
            '.product-details',
            '.description',
            '.product-info .description',
            '[data-testid="description"]',
            '.product-content',
            '.product-summary'
        ]
        
        for selector in description_selectors:
            desc_element = soup.select_one(selector)
            if desc_element:
                # Remove any nested price or button elements
                for unwanted in desc_element.find_all(['button', 'a', '.price', '.btn']):
                    unwanted.decompose()
                
                description = self._clean_text(desc_element.get_text())
                if description and len(description) > 20:
                    return description
        
        return None
    
    def _extract_promotion_info(self, soup) -> Dict[str, Any]:
        """Extract promotion and discount information with validity periods."""
        promotion_info = {}
        
        # Look for discount/promotion sections
        promo_selectors = [
            '.promotion',
            '.discount',
            '.offer',
            '.sale',
            '.special-price',
            '.promo-banner',
            '.price-reduction'
        ]
        
        for selector in promo_selectors:
            promo_element = soup.select_one(selector)
            if promo_element:
                promo_text = self._clean_text(promo_element.get_text())
                
                if promo_text:
                    # Extract discount percentage or amount
                    percent_match = re.search(r'(\d+)\s*%', promo_text)
                    amount_match = re.search(r'(\d+[.,]?\d*)\s*(лв|BGN)', promo_text)
                    
                    promotion_info['discount'] = {
                        'text': promo_text,
                        'percentage': percent_match.group(1) if percent_match else None,
                        'amount': amount_match.group(1) if amount_match else None
                    }
                    
                    break
        
        return promotion_info
    
    def _extract_detailed_availability(self, soup) -> str:
        """Extract detailed availability information from product page."""
        availability_selectors = [
            '.availability',
            '.stock-status',
            '.product-availability',
            '[data-testid="availability"]',
            '.inventory-status'
        ]
        
        for selector in availability_selectors:
            avail_element = soup.select_one(selector)
            if avail_element:
                avail_text = self._clean_text(avail_element.get_text()).lower()
                
                if any(word in avail_text for word in ['налич', 'в наличност', 'available', 'in stock']):
                    return 'Налично'
                elif any(word in avail_text for word in ['изчерп', 'няма', 'out of stock', 'unavailable']):
                    return 'Неналично'
                elif any(word in avail_text for word in ['скоро', 'очаква', 'coming soon', 'expected']):
                    return 'Очаква се'
        
        return 'Неизвестно'
