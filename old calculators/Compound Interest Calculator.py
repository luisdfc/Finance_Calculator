import matplotlib.pyplot as plt
import numpy as np
import sys

# --- Fórmulas de Interés Compuesto ---

def calculate_future_value(principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning):
    """Calcula el valor futuro de una inversión con aportaciones periódicas."""
    if periods_per_year == 0: return principal
    
    rate_per_period = (annual_rate / 100) / periods_per_year
    num_periods = years * periods_per_year

    # FV del principal
    fv_principal = principal * ((1 + rate_per_period) ** num_periods)

    # FV de las aportaciones (anualidad)
    if rate_per_period > 0:
        fv_deposits = periodic_deposit * (((1 + rate_per_period) ** num_periods - 1) / rate_per_period)
        if deposit_at_beginning:
            fv_deposits *= (1 + rate_per_period)
    else: # Si no hay interés, es solo la suma de las aportaciones
        fv_deposits = periodic_deposit * num_periods
        
    return fv_principal + fv_deposits

# --- Funciones para la Gráfica ---

def plot_investment_growth(history):
    """Genera y muestra una gráfica del crecimiento de la inversión."""
    if not history:
        print("No hay datos para graficar.")
        return

    years = [item['year'] for item in history]
    principal = [item['principal'] for item in history]
    total_deposits = [item['total_deposits'] for item in history]
    interest_earned = [item['interest_earned'] for item in history]

    # Usamos numpy para apilar las barras
    principal = np.array(principal)
    total_deposits = np.array(total_deposits)
    interest_earned = np.array(interest_earned)

    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(12, 7))

    # Gráfica de barras apiladas
    ax.bar(years, principal, label='Balance Inicial', color='#003f5c')
    ax.bar(years, total_deposits, bottom=principal, label='Aportaciones Totales', color='#7a5195')
    ax.bar(years, interest_earned, bottom=principal + total_deposits, label='Intereses Generados', color='#ffa600')

    ax.set_title('Crecimiento de la Inversión a lo Largo del Tiempo', fontsize=16, fontweight='bold')
    ax.set_xlabel('Años', fontsize=12)
    ax.set_ylabel('Balance (€)', fontsize=12)
    ax.legend()
    
    # Formatear el eje Y para mostrar valores monetarios
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    # Asegurarse de que los años se muestren como enteros
    if len(years) > 10:
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

    plt.tight_layout()
    print("\nCerrando la ventana de la gráfica para continuar...")
    plt.show()

# --- Funciones de Entrada de Usuario ---

def get_common_inputs(ask_for):
    """Obtiene las entradas comunes del usuario."""
    inputs = {}
    
    if 'initial' in ask_for:
        inputs['principal'] = float(input("Balance Inicial (€): "))
    if 'deposit' in ask_for:
        inputs['periodic_deposit'] = float(input("Depósito Periódico (€): "))
    if 'frequency' in ask_for:
        freq_options = {'1': 52, '2': 26, '3': 12, '4': 1}
        freq_choice = input("Frecuencia del Periodo (1: Semanal, 2: Bi-Semanal, 3: Mensual, 4: Anual): ")
        inputs['periods_per_year'] = freq_options.get(freq_choice, 12)
    if 'timing' in ask_for:
        timing_choice = input("¿Depósitos al inicio o al final del periodo? (1: Inicio, 2: Final): ")
        inputs['deposit_at_beginning'] = (timing_choice == '1')
    if 'rate' in ask_for:
        inputs['annual_rate'] = float(input("Ratio Interés Anual (%): "))
    if 'duration' in ask_for:
        inputs['years'] = int(input("Duración (en años): "))
    if 'goal' in ask_for:
        inputs['goal'] = float(input("Objetivo de Ahorro (€): "))
        
    return inputs

# --- Lógica de la Calculadora ---

def option_calculate_balance():
    """Calcula y muestra el balance final y la gráfica de crecimiento."""
    print("\n--- 1. Calcular Balance Final ---")
    print("Introduce los datos de tu inversión para proyectar el resultado final.")
    
    try:
        params = get_common_inputs(['initial', 'deposit', 'frequency', 'timing', 'rate', 'duration'])
        
        history = []
        for year in range(params['years'] + 1):
            balance = calculate_future_value(params['principal'], params['annual_rate'], year, params['periods_per_year'], params['periodic_deposit'], params['deposit_at_beginning'])
            total_deposits = params['periodic_deposit'] * params['periods_per_year'] * year
            interest = balance - params['principal'] - total_deposits
            history.append({
                'year': year,
                'balance': balance,
                'principal': params['principal'],
                'total_deposits': total_deposits,
                'interest_earned': interest
            })

        final_balance = history[-1]['balance']
        print("\n--- Resultado ---")
        print(f"Tras {params['years']} años, tu balance final será: {final_balance:,.2f} €")
        
        plot_investment_growth(history)

    except ValueError:
        print("\nError: Entrada inválida. Por favor, introduce solo números.")

def option_calculate_time():
    """Calcula el tiempo necesario para alcanzar un objetivo de ahorro."""
    print("\n--- 2. Calcular Tiempo para Alcanzar Objetivo ---")
    print("Introduce tu objetivo para saber cuántos años tardarás en alcanzarlo.")
    
    try:
        params = get_common_inputs(['initial', 'deposit', 'frequency', 'timing', 'rate', 'goal'])
        
        if params['principal'] >= params['goal']:
            print("\n¡Felicidades! Ya has alcanzado tu objetivo con tu balance inicial.")
            return

        years = 0
        balance = params['principal']
        history = []
        max_years = 100 # Límite para evitar bucles infinitos

        while balance < params['goal'] and years <= max_years:
            total_deposits = params['periodic_deposit'] * params['periods_per_year'] * years
            interest = balance - params['principal'] - total_deposits
            history.append({
                'year': years,
                'balance': balance,
                'principal': params['principal'],
                'total_deposits': total_deposits,
                'interest_earned': interest
            })
            years += 1
            balance = calculate_future_value(params['principal'], params['annual_rate'], years, params['periods_per_year'], params['periodic_deposit'], params['deposit_at_beginning'])

        print("\n--- Resultado ---")
        if years > max_years:
            print(f"No se ha alcanzado el objetivo de {params['goal']:,.2f} € en {max_years} años.")
        else:
            print(f"Necesitarás aproximadamente {years} años para alcanzar tu objetivo de {params['goal']:,.2f} €.")
            plot_investment_growth(history)
            
    except ValueError:
        print("\nError: Entrada inválida. Por favor, introduce solo números.")


def option_calculate_rate():
    """Calcula la tasa de interés necesaria para alcanzar un objetivo."""
    print("\n--- 3. Calcular Tasa de Interés Requerida ---")
    print("Introduce tu objetivo y el plazo para saber qué rentabilidad necesitas.")
    
    try:
        params = get_common_inputs(['initial', 'deposit', 'frequency', 'timing', 'duration', 'goal'])
        
        # Búsqueda de la tasa por aproximación (búsqueda binaria)
        low_rate, high_rate = 0.0, 100.0
        required_rate = -1
        
        for _ in range(100): # 100 iteraciones para precisión
            mid_rate = (low_rate + high_rate) / 2
            balance = calculate_future_value(params['principal'], mid_rate, params['years'], params['periods_per_year'], params['periodic_deposit'], params['deposit_at_beginning'])
            
            if abs(balance - params['goal']) < 0.01:
                required_rate = mid_rate
                break
            elif balance < params['goal']:
                low_rate = mid_rate
            else:
                high_rate = mid_rate
        
        required_rate = (low_rate + high_rate) / 2 # Mejor aproximación final
        
        print("\n--- Resultado ---")
        print(f"Para alcanzar {params['goal']:,.2f} € en {params['years']} años, necesitas una tasa de interés anual de aprox. {required_rate:.2f}%.")
        
        # Generar gráfica con la tasa encontrada
        history = []
        for year in range(params['years'] + 1):
            balance = calculate_future_value(params['principal'], required_rate, year, params['periods_per_year'], params['periodic_deposit'], params['deposit_at_beginning'])
            total_deposits = params['periodic_deposit'] * params['periods_per_year'] * year
            interest = balance - params['principal'] - total_deposits
            history.append({
                'year': year, 'balance': balance, 'principal': params['principal'],
                'total_deposits': total_deposits, 'interest_earned': interest
            })
        plot_investment_growth(history)

    except ValueError:
        print("\nError: Entrada inválida. Por favor, introduce solo números.")


def option_calculate_deposit():
    """Calcula la aportación periódica necesaria para alcanzar un objetivo."""
    print("\n--- 4. Calcular Depósito Periódico Requerido ---")
    print("Introduce tu objetivo para saber cuánto necesitas aportar periódicamente.")
    
    try:
        params = get_common_inputs(['initial', 'frequency', 'timing', 'rate', 'duration', 'goal'])
        
        rate_per_period = (params['annual_rate'] / 100) / params['periods_per_year']
        num_periods = params['years'] * params['periods_per_year']
        
        # FV del principal
        fv_principal = params['principal'] * ((1 + rate_per_period) ** num_periods)
        
        # FV necesario de las aportaciones
        required_fv_from_deposits = params['goal'] - fv_principal
        
        if required_fv_from_deposits < 0:
            print("\nTu balance inicial por sí solo superará el objetivo. No necesitas hacer aportaciones.")
            return
        
        # Calculamos el PMT (pago periódico)
        if rate_per_period > 0:
            denominator = (((1 + rate_per_period) ** num_periods - 1) / rate_per_period)
            if params['deposit_at_beginning']:
                denominator *= (1 + rate_per_period)
            
            if denominator == 0:
                required_deposit = 0
            else:
                required_deposit = required_fv_from_deposits / denominator
        else:
            required_deposit = required_fv_from_deposits / num_periods

        print("\n--- Resultado ---")
        print(f"Para alcanzar {params['goal']:,.2f} € en {params['years']} años, necesitas un depósito periódico de {required_deposit:,.2f} €.")
        
        # Generar gráfica con la aportación encontrada
        history = []
        for year in range(params['years'] + 1):
            balance = calculate_future_value(params['principal'], params['annual_rate'], year, params['periods_per_year'], required_deposit, params['deposit_at_beginning'])
            total_deposits = required_deposit * params['periods_per_year'] * year
            interest = balance - params['principal'] - total_deposits
            history.append({
                'year': year, 'balance': balance, 'principal': params['principal'],
                'total_deposits': total_deposits, 'interest_earned': interest
            })
        plot_investment_growth(history)

    except ValueError:
        print("\nError: Entrada inválida. Por favor, introduce solo números.")


# --- Menú Principal ---

def main():
    """Función principal que muestra el menú y gestiona las opciones."""
    while True:
        print("\n" + "="*40)
        print("    Calculadora de Interés Compuesto")
        print("="*40)
        print("Visualiza tu futuro financiero al invertir.")
        print("\nElige una opción:")
        print("  1. Calcular Balance Final")
        print("  2. Calcular Tiempo para Alcanzar Objetivo")
        print("  3. Calcular Tasa de Interés Requerida")
        print("  4. Calcular Depósito Periódico Requerido")
        print("  5. Salir")

        choice = input("\nTu elección: ")

        if choice == '1':
            option_calculate_balance()
        elif choice == '2':
            option_calculate_time()
        elif choice == '3':
            option_calculate_rate()
        elif choice == '4':
            option_calculate_deposit()
        elif choice == '5':
            print("¡Hasta la próxima!")
            sys.exit()
        else:
            print("Opción no válida. Por favor, elige un número del 1 al 5.")

if __name__ == "__main__":
    main()