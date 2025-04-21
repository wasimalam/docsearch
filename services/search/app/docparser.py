import docx
class docparser:
    def __init__(self, path) :
        doc = docx.Document(path)
        core_properties = doc.core_properties
        self.title = core_properties.title
        self.subject= core_properties.subject
        self.author= core_properties.author
        self.keywords= core_properties.keywords
        self.comments= core_properties.comments
        self.last_modified_by= core_properties.last_modified_by
        self.created= core_properties.created,
        self.modified= core_properties.modified
        self.language= core_properties.language
        self.content=self.getText(doc)

    def getText(self, doc):
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return '\n'.join(fullText)
        