from dataclasses import dataclass
from typing import Sequence, Optional

from utilities.choices import ButtonColorChoices


__all__ = (
    'get_model_item',
    'get_model_buttons',
    'Menu',
    'MenuGroup',
    'MenuItem',
    'MenuItemButton',
)


#
# Navigation menu data classes
#

@dataclass
class MenuItemButton:

    link: str
    title: str
    icon_class: str
    permissions: Optional[Sequence[str]] = ()
    color: Optional[str] = None


@dataclass
class MenuItem:

    link: str
    link_text: str
    permissions: Optional[Sequence[str]] = ()
    buttons: Optional[Sequence[MenuItemButton]] = ()


@dataclass
class MenuGroup:

    label: str
    items: Sequence[MenuItem]


@dataclass
class Menu:

    label: str
    icon_class: str
    groups: Sequence[MenuGroup]

    @property
    def name(self):
        return self.label.replace(' ', '_')


#
# Utility functions
#

def get_model_item(app_label, model_name, label, actions=('add', 'import')):
    return MenuItem(
        link=f'{app_label}:{model_name}_list',
        link_text=label,
        permissions=[f'{app_label}.view_{model_name}'],
        buttons=get_model_buttons(app_label, model_name, actions)
    )


def get_model_buttons(app_label, model_name, actions=('add', 'import')):
    buttons = []

    if 'add' in actions:
        buttons.append(
            MenuItemButton(
                link=f'{app_label}:{model_name}_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                permissions=[f'{app_label}.add_{model_name}'],
                color=ButtonColorChoices.GREEN
            )
        )
    if 'import' in actions:
        buttons.append(
            MenuItemButton(
                link=f'{app_label}:{model_name}_import',
                title='Import',
                icon_class='mdi mdi-upload',
                permissions=[f'{app_label}.add_{model_name}'],
                color=ButtonColorChoices.CYAN
            )
        )

    return buttons
