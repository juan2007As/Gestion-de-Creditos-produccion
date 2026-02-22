"""
Tests para ALTO #2: Responsive Currency Inputs
Verifica que los inputs de moneda sean responsivos en todos los tamaños de pantalla
"""
from django.test import TestCase
from django.test.client import Client


class ResponsiveCurrencyInputsTests(TestCase):
    """Tests para verificar que currency inputs son responsivos"""
    
    def test_css_currency_classes_exist(self):
        """Verificar que las clases CSS para currency existen"""
        # Leer el archivo CSS
        with open('mi_app/static/mi_app/css/input-responsive.css', 'r') as f:
            css_content = f.read()
        
        # Verificar que existen las clases
        self.assertIn('.input-currency', css_content)
        self.assertIn('.currency-symbol', css_content)
        self.assertIn('@media (max-width: 480px)', css_content)
        self.assertIn('@media (min-width: 481px) and (max-width: 768px)', css_content)
        self.assertIn('@media (min-width: 769px)', css_content)
    
    def test_currency_css_has_mobile_styles(self):
        """Verificar que CSS tiene estilos para móvil"""
        with open('mi_app/static/mi_app/css/input-responsive.css', 'r') as f:
            css_content = f.read()
        
        # Móvil específicamente
        mobile_section = css_content[css_content.find('@media (max-width: 480px)'):
                                     css_content.find('@media (min-width: 481px)')]
        self.assertIn('min-width: 32px', mobile_section)
        self.assertIn('font-size: 12px', mobile_section)
    
    def test_currency_css_has_tablet_styles(self):
        """Verificar que CSS tiene estilos para tablet"""
        with open('mi_app/static/mi_app/css/input-responsive.css', 'r') as f:
            css_content = f.read()
        
        # Tablet específicamente
        tablet_section = css_content[css_content.find('@media (min-width: 481px) and (max-width: 768px)'):
                                     css_content.find('@media (min-width: 769px)')]
        self.assertIn('min-width: 40px', tablet_section)
        self.assertIn('font-size: 14px', tablet_section)
    
    def test_currency_css_has_desktop_styles(self):
        """Verificar que CSS tiene estilos para desktop"""
        with open('mi_app/static/mi_app/css/input-responsive.css', 'r') as f:
            css_content = f.read()
        
        # Desktop específicamente - debe estar después de tablet
        desktop_section = css_content[css_content.find('@media (min-width: 769px)'):]
        self.assertIn('min-width: 50px', desktop_section)
    
    def test_formulario_prestamo_uses_input_currency_class(self):
        """Verificar que formulario_prestamo.html usa clase input-currency"""
        with open('mi_app/templates/mi_app/formularios/formulario_prestamo.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Verificar que usa input-currency
        self.assertIn('class="input-currency"', template_content)
        self.assertIn('class="input-group-text currency-symbol"', template_content)
    
    def test_formulario_prestamo_monto_input_has_currency_symbol(self):
        """Verificar que input de monto tiene símbolo $"""
        with open('mi_app/templates/mi_app/formularios/formulario_prestamo.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Buscar sección de monto
        monto_section = template_content[template_content.find('id="monto_total"'):
                                         template_content.find('id="monto_total"') + 500]
        self.assertIn('<span class="input-group-text currency-symbol">$</span>', monto_section)
    
    def test_formulario_prestamo_interes_input_has_percent_symbol(self):
        """Verificar que input de interés tiene símbolo %"""
        with open('mi_app/templates/mi_app/formularios/formulario_prestamo.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Verificar que existe currency-symbol y % en la misma sección
        self.assertIn('currency-symbol', template_content)
        self.assertIn('>%<', template_content)  # El % está dentro de un span
    
    def test_currency_inputs_no_inline_styles(self):
        """Verificar que no hay estilos inline en currency symbols"""
        with open('mi_app/templates/mi_app/formularios/formulario_prestamo.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Verificar que NO hay style="width: 50px;" (cambio de ALTO #1)
        self.assertNotIn('style="width: 50px;"', template_content)
    
    def test_input_currency_display_flex(self):
        """Verificar que input-currency usa display: flex"""
        with open('mi_app/static/mi_app/css/input-responsive.css', 'r') as f:
            css_content = f.read()
        
        # Buscar sección de input-currency
        currency_section = css_content[css_content.find('.input-currency {'):
                                       css_content.find('.input-currency {') + 200]
        self.assertIn('display: flex', currency_section)
    
    def test_mobile_first_approach(self):
        """Verificar que CSS tiene estilos móviles responsivos"""
        with open('mi_app/static/mi_app/css/input-responsive.css', 'r') as f:
            css_content = f.read()
        
        # Verificar que existen todas las breakpoints
        self.assertIn('@media (max-width: 480px)', css_content)
        self.assertIn('@media (min-width: 481px) and (max-width: 768px)', css_content)
        self.assertIn('@media (min-width: 769px)', css_content)
    
    def test_currency_symbol_responsive_sizing(self):
        """Verificar que currency-symbol tiene tamaños diferentes por breakpoint"""
        with open('mi_app/static/mi_app/css/input-responsive.css', 'r') as f:
            css_content = f.read()
        
        # Conteo de min-width diferentes
        min_width_32 = css_content.count('min-width: 32px')  # móvil
        min_width_40 = css_content.count('min-width: 40px')  # tablet
        min_width_50 = css_content.count('min-width: 50px')  # desktop
        
        self.assertGreaterEqual(min_width_32, 1, "Debe tener min-width: 32px para móvil")
        self.assertGreaterEqual(min_width_40, 1, "Debe tener min-width: 40px para tablet")
        self.assertGreaterEqual(min_width_50, 1, "Debe tener min-width: 50px para desktop")
