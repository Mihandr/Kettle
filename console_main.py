import click
import kettle


@click.group()  # Группируем все функции
@click.option('--water', default=1, help='Количество воды вы чайнике.')  # Аргумент установки количества воды
@click.pass_context  # Переносим контекст
def main(ctx, water):
    """Комманда main для создания объекта чайника."""
    # необходимо убедится, что `ctx.obj`
    # существует и является словарем
    ctx.ensure_object(dict)
    k = kettle.Kettle(water)
    ctx.obj['class'] = k  # передаем контексту class


@main.command()  # Подкоманда группы команд
@click.pass_context  # Переносим контекст в подкоманду
def start(ctx):
    """Комманда start для включения чайника."""
    k = ctx.obj['class']
    k.button_start()


@main.command()  # Подкоманда группы команд
@click.option('--new_water', default=1, help='Новое количество воды.')  # Аргумент установки нового количества воды
@click.pass_context  # Переносим контекст в подкоманду
def top_up(ctx, new_water):
    """Комманда top_up для дополнения чайника водой."""
    k = ctx.obj['class']
    k.top_up(new_water)


@main.command()  # Подкоманда группы команд
@click.pass_context  # Переносим контекст в подкоманду
def params(ctx):
    """Комманда params для просмотра параметров чайника."""
    k = ctx.obj['class']
    k.help()


if __name__ == '__main__':
    main(obj={})



