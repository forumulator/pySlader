from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException


class SladerAgent:
    """ The slader agent, to browse slader.com and perform automations
        like upload	solutions
    """
    LOGIN_PAGE = "https://www.slader.com/account/login/"
    # TODO get a relative XPath for this
    SUBMIT_BUTTON = '/html/body/div[3]/section[3]/section/section[3]/section/form/input[2]'
    PAGE_NOT_FOUND = "Page Not Found"

    def __init__(self, user=None, passwd=None):
        # Disable images for faster loading of pages
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chromeOptions.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(chrome_options=chromeOptions)
        self.driver.implicitly_wait(5)
        # Login credentials
        self.creds = (user, passwd) if (user and passwd) else None

    def __enter__(self):
        self.login()
        return self

    def login(self):
        if self.creds:
            self.driver.get(SladerAgent.LOGIN_PAGE)
            login_form = self.driver.find_element_by_class_name("login")
            user_field, pass_field = login_form.find_element_by_id(
                "id_username"), login_form.find_element_by_id("id_password")
            # Enter creds
            user_field.send_keys(self.creds[0])
            pass_field.send_keys(self.creds[1])
            # Submit login information using the "Log In" button
            self.driver.find_element_by_xpath(SladerAgent.SUBMIT_BUTTON).click()
            return True
        else:
            return False

    def _put_text_in_elem(self, elem, text):
        """ Click input boc to make it active, and then send the
            text keys to the box.
        """
        while "with-toolbar" not in self.driver \
                .switch_to.active_element.get_attribute("class"):
            elem.click()
            time.sleep(0.5)
        time.sleep(1)
        # Actually put the text
        self.driver.switch_to.active_element.send_keys(text)
        # print(self.driver.switch_to.active_element.get_attribute("tag_name"),
        # self.driver.switch_to.active_element.get_attribute("class"))
        time.sleep(1)
        self._unselect_solution_row()

    # TODO Do this in a proper way
    def _unselect_solution_row(self):
        """ Unselect the currently active input box, by clicking
            on the add row button. Definitely not optimal :)
        """
        add_row = self.driver.find_element_by_class_name("add-row")
        for i in range(2):
            add_row.click()
        time.sleep(3)

    def _add_rows(self, num_rows):
        """ Add rows to make a total of num_rows rows """
        def page_num_rows(driver):
            return len(driver.find_elements_by_class_name("explanation-row"))
        # Add required rows
        tries = 0
        while page_num_rows(self.driver) < num_rows:
            try:
                self.driver.find_element_by_class_name("add-row").click()
            except NoSuchElementException as e:
                raise e
            except Exception as e:
                if tries == 50:
                    raise e
                else:
                    # For any other exception, like not clickable, just wait
                    time.sleep(2)
            tries += 1
            time.sleep(3)

    # TODO Make this work, it doesn't work right now
    def _give_five_stars(self):
        """ Rate the solution 5 stars """
        self.driver.find_elements_by_class_name("icon-star")[4].click()

    def _put_answer(self, answer):
        """ Put the answer in the solution box """
        self._add_rows(answer.rows)
        # Put solution in each row
        rows_elems = self.driver.find_elements_by_class_name("explanation-row")
        for i, row_text in enumerate(answer.rows):
            row = rows_elems[i]
            # Write solution in row
            self._put_text_in_elem(row.find_element_by_class_name(
                "explanation"), row_text)
        # Put Please view the explanation in the result box
        self._put_text_in_elem(self.driver.find_element_by_class_name(
            "result"), answer.RESULT_TEXT)

    def _submit_answer(self):
        """ Click the Submit button to submit the solution """
        # TODO This doesn't work, the finish_button.is_displayed() tests
        # true always. Why?
        finish_button = self.driver.find_element_by_class_name("finish")
        tries = 0
        while finish_button.is_displayed() and tries < 3:
            print("Submit button try: #" + str(tries))
            try:
                finish_button.click()
                time.sleep(2)
                finish_button = self.driver.find_element_by_class_name("finish")
            except (NoSuchElementException, ElementNotVisibleException) as e:
                raise e
            except Exception as e:
                pass
            finally:
                tries += 1

    def post_answer(self, answer):
        """ Post answer to the given problem """
        self.driver.get(answer.get_url())
        if SladerAgent.PAGE_NOT_FOUND in self.driver.title:
            raise ValueError("Invalid book details: " + str(answer.book.book))
        # Click the upload button
        try:
            self.driver.find_element_by_class_name("upload-solution").click()
        except (NoSuchElementException, ElementNotVisibleException):
            # Upload button not visible or solution already present
            raise Exception("Upload button doesn't exist, solution already uploaded")
        time.sleep(3)
        try:
            self._put_answer(answer)
            self._submit_answer()
        except Exception as e:
            print(str(e))
            raise Exception("Error posting answer: " + str(answer))
        # Click the submit button to post solution
        time.sleep(1)
        return True

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.driver.close()
