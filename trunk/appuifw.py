#!/usr/bin/python
# Copyright (c) 2009 Marcelo Barros de Almeida
#                    marcelobarrosalmeida@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from PyQt4 import QtGui, QtCore

def note(text,note_type=u'info',global_note=0):
    note_types = {u'info':QtGui.QMessageBox.information,
                  u'conf':QtGui.QMessageBox.warning,
                  u'error':QtGui.QMessageBox.critical}
    if note_type not in note_types.keys():
        raise ValueError
    note_types[note_type](None, note_type, text);
     
class Icon():
    def __init__(self,filename, bitmap, bitmap_mask):
        self.filename = filename
        self.bitmap = bitmap
        self.bitmap_mask = bitmap_mask
        
class Listbox(QtGui.QListWidget):
    SINGLE, SINGLE_WITH_ICONS, DOUBLE, DOUBLE_WITH_ICONS = range(1,5)
    def __init__(self, items, callback=None, parent=None):
        self.callback = callback
        QtGui.QListWidget.__init__(self, parent)
        self.set_list(items)
        self.connect(self,
                     QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem*)'),
                     self.__item_clicked)

    def __process_items(self,items):
        if not items:
            raise Exception(u'Listbox contents can not be empty')
        elif isinstance(items[0],unicode):
            self.list_type = Listbox.SINGLE
            items_processed = items
        elif isinstance(items[0][1],Icon):
            self.list_type = Listbox.SINGLE_WITH_ICONS
            items_processed = [ a for a,b in items ]
        elif isinstance(items[0][1],unicode) and len(items[0]) == 2:
            self.list_type = Listbox.DOUBLE
            items_processed = [ "%s\n%s" % (a,b) for a,b in items ]
        else:
            self.list_type = Listbox.DOUBLE_WITH_ICONS
            items_processed = [ "%s\n%s" % (a,b) for a,b,c in items ]
            
        return items_processed
            
    def __item_clicked(self,item):
        if self.callback:
            self.callback()

    def bind(self,event_code,callback):
        pass
    
    def current(self):
        return self.currentRow()
    
    def set_list(self,items,current=0):
        self.items = self.__process_items(items)
        self.clear()
        self.addItems(self.items)
        self.setCurrentRow(current)
        
    def size(self):
        return (self.width,self.height)
    
    def position(self):
        return (self.x,self.y)

class Text(QtGui.QTextEdit):
    def __init__(self, text=u'', parent=None):
        QtGui.QTextEdit.__init__(self, text, parent)

    def add(self,text):
        self.setText(self.toPlainText()+text)

    def bind(self, event_code, callback):
        pass

    def clear(self):
        QtGui.QTextEdit.clear(self)

    def delete(self, pos=0, length=-1):
        text = self.toPlainText()
        if length == -1:
            length = len(text) - pos
        self.setText(text[:pos] + text[pos+length:])
        # TODO: try to implement using cursors        
    
    def get_pos(self):
        return self.textCursor().position()
        
    def len(self):
        return len(self.toPlainText())

    def get(self, pos=0, length=-1):
        text = self.toPlainText()
        if length == -1:
            length = len(text) - pos        
        return text[pos:pos+length]

    def set(self,text):
        self.setText(text)

    def set_pos(self,cursor_pos):
        tc = self.textCursor()
        tc.setPosition(cursor_pos)
        self.setTextCursor(tc)


class Canvas(QtGui.QWidget):
    def __init__(self, parent=None, text=u''):
        QtGui.QWidget.__init__(self, parent)

class PopupMenu(QtGui.QDialog):
    def __init__(self, parent=None,):
        QtGui.QDialog.__init__(self, parent)
        self.__init_app_win()
        
    def __init_app_win(self):
        self.__ok_but = QtGui.QPushButton(u'Ok',self)
        self.__cancel_but = QtGui.QPushButton(u'Cancel',self)        
        self.__list = QtGui.QListWidget(self)
        self.__grid = QtGui.QGridLayout(self)
        self.__grid.addWidget(self.__list,0,0,4,2)
        self.__grid.addWidget(self.__ok_but,4,0)
        self.__grid.addWidget(self.__cancel_but,4,1)        
        self.setLayout(self.__grid)
        self.setModal(True)
        self.connect(self,
                     QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem*)'),
                     self.__ok_but_clicked)
        self.connect(self.__ok_but,
                     QtCore.SIGNAL('clicked()'),
                     self.__ok_but_clicked)
        self.connect(self.__cancel_but,
                     QtCore.SIGNAL('clicked()'),
                     self.__cancel_but_clicked)   

    def __ok_but_clicked(self):
        self.done(self.__list.currentRow())

    def __cancel_but_clicked(self):
        self.done(-1)

    def exec_(self,menu_options,title):
        self.setWindowTitle(title)
        self.__list.clear()
        if isinstance(menu_options[0],tuple):
            items = [ "%s\n%s" % (a,b) for a,b in menu_options ]
        else:
            items = menu_options
        self.__list.addItems(items)
        ret = QtGui.QDialog.exec_(self)
        if ret == -1:
            return None
        else:
            return ret
        
class SelectionList(QtGui.QDialog):
    def __init__(self, parent=None,):
        QtGui.QDialog.__init__(self, parent)
        self.__init_app_win()
        
    def __init_app_win(self):
        self.__ok_but = QtGui.QPushButton(u'Ok',self)
        self.__cancel_but = QtGui.QPushButton(u'Cancel',self)
        self.__list = QtGui.QListWidget(self)
        self.__search = QtGui.QLineEdit(self)
        self.__grid = QtGui.QGridLayout(self)
        self.__grid.addWidget(self.__list,0,0,4,2)
        self.__grid.addWidget(self.__search,4,0,1,2)
        self.__grid.addWidget(self.__ok_but,5,0)
        self.__grid.addWidget(self.__cancel_but,5,1)
        self.__indexes = []
        self.__items = []
        self.__search_field = False
        self.setLayout(self.__grid)
        self.setModal(True)
        self.connect(self,
                     QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem*)'),
                     self.__ok_but_clicked)
        self.connect(self.__ok_but,
                     QtCore.SIGNAL('clicked()'),
                     self.__ok_but_clicked)
        self.connect(self.__cancel_but,
                     QtCore.SIGNAL('clicked()'),
                     self.__cancel_but_clicked)   
        self.connect(self.__search,
                     QtCore.SIGNAL('textChanged(const QString&)'),
                     self.__search_changed)
        
    def __ok_but_clicked(self):
        self.done(self.__list.currentRow())

    def __cancel_but_clicked(self):
        self.done(-1)

    def __search_changed(self):
        items = []
        indxs = []
        search = self.__search.text()
        for n in xrange(len(self.__items)):
            item = self.__items[n]
            if item.find(search) >= 0:
                items.append(item)
                indxs.append(n)
        self.__indexes = indxs
        self.__list.clear()
        self.__list.addItems(items)
    
    def exec_(self,items,search_field=False):
        self.__search_field = search_field
        self.setWindowTitle(u"")
        self.__search.setText(u"")
        self.__list.clear()
        self.__list.addItems(items)
        self.__indexes = range(len(items))
        self.__items = items
        if self.__search_field:
              self.__search.show()
              self.__grid.addWidget(self.__list,0,0,4,2)
              self.__grid.addWidget(self.__search,4,0,1,2)
        else:
              self.__search.hide()
              self.__grid.addWidget(self.__list,0,0,5,2)
        ret = QtGui.QDialog.exec_(self)
        if ret == -1:
            return None
        else:
            return self.__indexes[ret]
    
class PyS60App(QtGui.QWidget):
    def __init__(self, parent=None, title=u'', size=(240,320)):
        self.__app = QtGui.QApplication(sys.argv)
        QtGui.QWidget.__init__(self, parent)
        self.title = title
        self.size = size
        self.__menu_but = None
        self.__exit_but = None
        self.__grid = None
        self.__init_app_win()

    def __setattr__(self,k,v):
        """ Add special handling for app attributes, like
            menu, body, exit_handler.
        """
        if k == 'body':
            self.body.deleteLater()
            QtGui.QWidget.__setattr__(self,k,v)
            self.__grid.addWidget(self.body,0,0,5,5)
        elif k == 'menu':
            self.__build_menu(v)
            QtGui.QWidget.__setattr__(self,k,v)
        elif k == 'title':
            QtGui.QWidget.__setattr__(self,k,v)
            self.setWindowTitle(self.title)
        else:
            QtGui.QWidget.__setattr__(self,k,v)

    def __init_app_win(self):
        self.setWindowTitle(self.title)
        self.__grid = QtGui.QGridLayout(self)
        self.__menu_but = QtGui.QPushButton(u'Menu',self)
        self.__exit_but = QtGui.QPushButton(u'Exit',self)
        # Creates self.body but avoid local __setattr__ at first time
        QtGui.QWidget.__setattr__(self,'body',Canvas(self))
        QtGui.QWidget.__setattr__(self,'menu',[])
        self.__grid.addWidget(self.body,0,0,5,5)
        self.__grid.addWidget(self.__menu_but,5,0)
        self.__grid.addWidget(self.__exit_but,5,4)
        self.setLayout(self.__grid)
        self.resize(self.size[0],self.size[1])
        self.connect(self.__exit_but,
                     QtCore.SIGNAL('clicked()'),
                     self.__exit_but_clicked)
        self.connect(self.__menu_but,
                     QtCore.SIGNAL('clicked()'),
                     self.__menu_but_clicked)          
        self.show()

    def __exit_but_clicked(self):
        self.emit(QtCore.SIGNAL('close()'))
        self.__app.quit()

    def set_exit(self):
        self.__exit_but_clicked()

    def wait_app(self):
        sys.exit(self.__app.exec_())

    def __menu_but_clicked(self):
        self.__menu_but.showMenu()
        
    def __build_menu(self,menu_items):
        menu = QtGui.QMenu(self)
        for menu_label,menu_callback in menu_items:
            if isinstance(menu_callback,tuple):
                sub_menu = QtGui.QMenu(self)
                for sub_menu_label,sub_menu_callback in menu_callback:
                    item = QtGui.QAction(sub_menu_label,self)
                    self.connect(item, QtCore.SIGNAL('triggered()'), sub_menu_callback)
                    sub_menu.addAction(item)
                qa = menu.addMenu(sub_menu)
                qa.setText(menu_label)
            else:
                item = QtGui.QAction(menu_label,self)
                self.connect(item, QtCore.SIGNAL('triggered()'), menu_callback)
                menu.addAction(item)
        self.__menu_but.setMenu(menu)

app = PyS60App()
__popup_menu = PopupMenu()
__selection_list = SelectionList()

def popup_menu(options,title):
    if not options:
        raise Exception(u"Option list can not be empty")
    return __popup_menu.exec_(options,title)

def selection_list(options,search_field=False):
    if not options:
        raise Exception(u"Option list can not be empty")
    return __selection_list.exec_(options,search_field)

if __name__ == "__main__":

    def popup_menu_test():
        import random
        m = random.randint(1,20)
        if m % 2:
            op = [ u"Option %d" % n for n in xrange(m) ]
        else:
            op = [ (u"Option %d" % n,u"Second line") for n in xrange(m) ]
        title = u'Your option %d' % m
        print "selected ->",popup_menu(op,title)
        
    def selection_list_test():
        import random
        m = random.randint(1,20)
        op = [ u"Option %d" % n for n in xrange(m) ]
        sf = m % 2 == 0
        print "selected ->",selection_list(op,sf)

    def new_text_body():
        global app
        app.body = Text()
        app.title = u"Text body"

    def note_test(t):
        note(u"Note example",t)
        
    def new_listbox_body(tp):
        global app
        app.title = u"Listbox body type %d" % tp
        if tp == 0:
            lb = Listbox([u"Item 1",
                          u"Item 2",
                          u"Item 3",
                          u"Item 4",
                          u"Item 5"])
        elif tp == 1:
            lb = Listbox([(u"Item a",Icon(None,None,None)),
                          (u"Item b",Icon(None,None,None)),
                          (u"Item c",Icon(None,None,None)),
                          (u"Item d",Icon(None,None,None)),
                          (u"Item e",Icon(None,None,None))])
        elif tp == 2:
            lb = Listbox([(u"Item 1",u"Second line"),
                          (u"Item 2",u"Second line"),
                          (u"Item 3",u"Second line"),
                          (u"Item 4",u"Second line"),
                          (u"Item 5",u"Second line")])
        elif tp == 3:
            lb = Listbox([(u"Item a",u"Second line",Icon(None,None,None)),
                          (u"Item b",u"Second line",Icon(None,None,None)),
                          (u"Item c",u"Second line",Icon(None,None,None)),
                          (u"Item d",u"Second line",Icon(None,None,None)),
                          (u"Item e",u"Second line",Icon(None,None,None))])
        app.body = lb
        
    app.title = u"appuifw demo"
    app.menu = [(u'Text body', new_text_body),
                (u'Listbox body',((u'single',lambda:new_listbox_body(0)),
                                  (u'single w/ icons',lambda:new_listbox_body(1)),
                                  (u'double',lambda:new_listbox_body(2)),
                                  (u'double w/ icons',lambda:new_listbox_body(3)))),
                (u'popup_menu',popup_menu_test),
                (u'note',((u'info',lambda:note_test(u'info')),
                          (u'error',lambda:note_test(u'error')),
                          (u'conf',lambda:note_test(u'conf')))),
                (u'selection_list',selection_list_test),
                (u'Exit', lambda: app.set_exit())]

    app.wait_app()
