        WikiFunctions.Parse.Parsers parsers = new WikiFunctions.Parse.Parsers();
        WikiFunctions.Parse.HideText removeText = new WikiFunctions.Parse.HideText(false, true, false);
        WikiFunctions.Parse.HideText HiderHideExtLinksImages = new WikiFunctions.Parse.HideText(true, true, true);

        WikiFunctions.Parse.HideText HiderHideExtLinksImagesUnhideMeta = new WikiFunctions.Parse.HideText(true, false, true);

        /// <summary>
        /// Sửa lỗi chung của AWB
        /// </summary>
        /// <param name="ArticleText"></param>
        /// <param name="ArticleTitle"></param>
        /// <param name="wikiNamespace"></param>
        /// <param name="Summary"></param>
        /// <param name="Skip"></param>
        /// <returns></returns>
        public string ProcessArticle(string ArticleText, string ArticleTitle, int wikiNamespace, out string Summary, out bool Skip)
        {
            Skip = false;
            Summary = "";

            Article a = new Article(ArticleTitle, ArticleText);

            string zeroth = WikiRegexes.ZerothSection.Match(a.ArticleText).Value;
            bool CircaLink = WikiRegexes.CircaLinkTemplate.IsMatch(a.ArticleText), Floruit = (!zeroth.Contains(@"[[floruit|fl.]]") && WikiRegexes.UnlinkedFloruit.IsMatch(zeroth));

            /*a.HideMoreText(HiderHideExtLinksImages);

            // The two slashes below are inserted to disable the insertion of non-breaking spaces HTML markup (sample) 
            // a.AWBChangeArticleText("Fix non-breaking spaces", parsers.FixNonBreakingSpaces(a.ArticleText), true);

            a.AWBChangeArticleText("Mdashes", parsers.Mdashes(a.ArticleText, ArticleTitle), true);

            a.AWBChangeArticleText("Fix Date Ordinals/Of", parsers.FixDateOrdinalsAndOf(a.ArticleText, ArticleTitle), true, true);


            a.AWBChangeArticleText("FixBrParagraphs", parsers.FixBrParagraphs(a.ArticleText).Trim(), true);

            if (!Tools.IsRedirect(a.ArticleText))
            {
                a.AWBChangeArticleText("Fix dates 1", parsers.FixDatesB(a.ArticleText, CircaLink, Floruit).Trim(), true);
            }

            a.UnHideMoreText(HiderHideExtLinksImages);

            if (!Tools.IsRedirect(a.ArticleText))
            {
                // FixDates does its own hiding
                a.AWBChangeArticleText("Fix dates 2", parsers.FixDatesA(a.ArticleText).Trim(), true);
            }

            a.HideText(removeText);

            if (Tools.IsRedirect(a.ArticleText))
            {
                a.AWBChangeArticleText("Redirect tagger", WikiFunctions.Parse.Parsers.RedirectTagger(a.ArticleText, ArticleTitle), true);

                a.AWBChangeArticleText("Fix syntax redirects", WikiFunctions.Parse.Parsers.FixSyntaxRedirects(a.ArticleText), true);
            }
            else
            {
                a.AWBChangeArticleText("Template redirects", WikiFunctions.Parse.Parsers.TemplateRedirects(a.ArticleText, WikiRegexes.TemplateRedirects), true);

                a.AWBChangeArticleText("Fixes for {{Multiple issues}}", parsers.MultipleIssues(a.ArticleText), true);

                a.AWBChangeArticleText("Fix whitespace in links", WikiFunctions.Parse.Parsers.FixLinkWhitespace(a.ArticleText, ArticleTitle), true);

                a.AWBChangeArticleText("Fix syntax", WikiFunctions.Parse.Parsers.FixSyntax(a.ArticleText), true, true);

                a.AWBChangeArticleText("Rename Template Parameters", WikiFunctions.Parse.Parsers.RenameTemplateParameters(a.ArticleText, WikiRegexes.RenamedTemplateParameters), true);

                a.EmboldenTitles(parsers, false);

                a.AWBChangeArticleText("Conversions", WikiFunctions.Parse.Parsers.Conversions(a.ArticleText), true);
                a.AWBChangeArticleText("FixLivingThingsRelatedDates", WikiFunctions.Parse.Parsers.FixLivingThingsRelatedDates(a.ArticleText), true);
                a.AWBChangeArticleText("FixHeadings", WikiFunctions.Parse.Parsers.FixHeadings(a.ArticleText, ArticleTitle), true);

                a.FixPeopleCategories(parsers, false);

                a.SetDefaultSort(Variables.LangCode, false, false);

                a.AWBChangeArticleText("Fix categories", WikiFunctions.Parse.Parsers.FixCategories(a.ArticleText), true);

                a.AWBChangeArticleText("Fix images", WikiFunctions.Parse.Parsers.FixImages(a.ArticleText), true);

                a.BulletExternalLinks(false);

                a.CiteTemplateDates(parsers, false);

                a.AWBChangeArticleText("Fix citation templates", WikiFunctions.Parse.Parsers.FixCitationTemplates(a.ArticleText), true, true);

                a.AWBChangeArticleText("Fix temperatures", WikiFunctions.Parse.Parsers.FixTemperatures(a.ArticleText), true);

                a.AWBChangeArticleText("Fix main article", WikiFunctions.Parse.Parsers.FixMainArticle(a.ArticleText), true);

                if (a.IsMissingReferencesDisplay && !Variables.LangCode.Equals("de"))
                    a.AWBChangeArticleText("Fix reference tags", WikiFunctions.Parse.Parsers.FixReferenceListTags(a.ArticleText), true);

                a.AWBChangeArticleText("Fix empty links and templates", WikiFunctions.Parse.Parsers.FixEmptyLinksAndTemplates(a.ArticleText), true);

                a.AWBChangeArticleText("Fix empty references", WikiFunctions.Parse.Parsers.SimplifyReferenceTags(a.ArticleText), true);

                a.AWBChangeArticleText("DuplicateUnnamedReferences", WikiFunctions.Parse.Parsers.DuplicateUnnamedReferences(a.ArticleText), true);

                a.AWBChangeArticleText("DuplicateNamedReferences", WikiFunctions.Parse.Parsers.DuplicateNamedReferences(a.ArticleText), true);

                a.AWBChangeArticleText("SameRefDifferentName", WikiFunctions.Parse.Parsers.SameRefDifferentName(a.ArticleText), true);

                a.AWBChangeArticleText("Refs after punctuation", WikiFunctions.Parse.Parsers.RefsAfterPunctuation(a.ArticleText), true);

                a.AWBChangeArticleText("ReorderReferences", WikiFunctions.Parse.Parsers.ReorderReferences(a.ArticleText), true);

                a.AWBChangeArticleText("FixReferenceTags", WikiFunctions.Parse.Parsers.FixReferenceTags(a.ArticleText), true);

                //Module cho tiếng Anh
                //a.AWBChangeArticleText("Add missing {{reflist}}", WikiFunctions.Parse.Parsers.AddMissingReflist(a.ArticleText), true, true);

                //a.AWBChangeArticleText("PersonData", WikiFunctions.Parse.Parsers.PersonData(a.ArticleText, ArticleTitle), true);

                //int bracketLength;
                //string place = String.Empty;

                //if (WikiFunctions.Parse.Parsers.UnbalancedBrackets(a.ArticleText, out bracketLength) >= 0)
                //{
                //    place = a.ArticleText.Substring(bracketLength - 10, bracketLength + 10);
                //    a.AWBChangeArticleText("UnbalancedBrackets","{{thế:Mất cân bằng thẻ|" + place + "}}" + a.ArticleText, true);
                //}

             * 

                a.FixLinks(false);

                a.AWBChangeArticleText("Simplify links", WikiFunctions.Parse.Parsers.SimplifyLinks(a.ArticleText), true);
            }

            a.UnHideText(removeText);
            */

            //a.AWBChangeArticleText("Sort meta data", parsers.SortMetaData(a.ArticleText, ArticleTitle), true);

            a.AWBChangeArticleText("ViWikiFixes", ViWikiFixes(a.ArticleText, ArticleTitle, wikiNamespace), true);

            //a.HideText(HiderHideExtLinksImagesUnhideMeta);

            //a.AWBChangeArticleText("Sửa ngày giờ", TranslateDateTime(a.ArticleText), true);

            //a.UnHideText(HiderHideExtLinksImagesUnhideMeta);

            return a.ArticleText;
        }

        /// <summary>
        /// Sửa lỗi chung cho tiếng Việt
        /// </summary>
        /// <param name="ArticleText"></param>
        /// <param name="ArticleTitle"></param>
        /// <param name="wikiNamespace"></param>
        /// <returns></returns>
        public string ViWikiFixes(string ArticleText, string ArticleTitle, int wikiNamespace)
        {
            //cấu hình các phương thức để chạy bot, dùng 2 dấu gạch chéo để che đi các phương thức không cần chạy
            string originVersion = ArticleText;

            // Choose main & category namespaces only
            if (wikiNamespace != 0 && wikiNamespace != 14)
            {
                return ArticleText;
            }


            ArticleText = TranslateBirthsDeathsCategory(ArticleText); // chạy lần 1

            ArticleText = TranslateDateTime(ArticleText); // dịch ngày giờ sang tiếng Việt

            ArticleText = TranslateCommon(ArticleText); // chạy lỗi chung (đa số sửa lỗi thông thường ở đây)

            ArticleText = PunctuationFixes(ArticleText, ArticleTitle); // sửa khoảng trắng trước dấu câu

            ArticleText = TranslateBirthsDeathsCategory(ArticleText); // chạy lần 2 để khỏi bị sót

            ArticleText = RemoveEnWikiInternalLink(ArticleText); // bỏ các liên kết với tiếng Anh (do Content Translation gây ra)

            // ArticleText = SetStub(ArticleText); // đặt bản mẫu sơ khai, tạm che

            ArticleText = SetReference(ArticleText, wikiNamespace); // đặt mục "Tham khảo" nếu bài chưa có

            return ArticleText;
        }

        /// <summary>
        /// Loại bỏ liên kết trong từ tiếng Anh
        /// </summary>
        /// <param name="ArticleText"></param>
        /// <returns></returns>
        public string RemoveEnWikiInternalLink(string ArticleText)
        {

            ArticleText = Regex.Replace(ArticleText, @"\[\[:en:", "[[");

            return ArticleText;
        }

        /// <summary>
        /// Dịch định dạng ngày giờ từ tiếng Anh sang tiếng Việt
        /// </summary>
        /// <param name="ArticleText"></param>
        /// <returns></returns>
        public string TranslateDateTime(string ArticleText)
        {

            if (ArticleText.Contains("xếp hạng đĩa đơn") || ArticleText.Contains("Xếp hạng đĩa đơn") || ArticleText.Contains("Singlechart") || ArticleText.Contains("singlechart")) return ArticleText;



            string a = "";
            string b = "";
            string c = "";
            string result = "";
            DateTime dt = new DateTime();
            string convertDate = ArticleText;
            string convertDatetemp = ArticleText;


            int count = 0;

            while (true)
            {
                if (count >= 100) break;
                count++;

                Match mdatetime = Regex.Match(convertDate, @"([Jj]anuary|[Ff]ebruary|[Mm]arch|[Aa]pril|[Mm]ay|[Jj]une|[Jj]uly|[Aa]ugust|[Ss]eptember|[Oo]ctober|[Nn]ovember|[Dd]ecember)\s{1}\d+,\s{1}\d{4}");

                if (mdatetime.Success)
                {

                    Match mfile = Regex.Match(convertDate.Substring(mdatetime.Index), @".*\.(jpg|JPG|jpeg|JPEG|gif|ogg|OGG|GIF|flac|FLAC|svg|SVG)");
                    if (mfile.Success && mfile.Value.Contains(mdatetime.Value) == true)
                    {
                        convertDate = convertDate.Substring(mfile.Index + mfile.Value.Length);
                        convertDatetemp = convertDate;
                        continue;
                    }
                    else
                    {

                        try
                        {
                            dt = Convert.ToDateTime(mdatetime.Value);
                            a = dt.Month.ToString();
                            b = dt.Day.ToString();
                            c = dt.Year.ToString();
                            result = "ngày " + b + " tháng " + a + " năm " + c;
                            convertDate = convertDate.Replace(mdatetime.Value, result);
                            ArticleText = ArticleText.Replace(convertDatetemp, convertDate);
                            convertDatetemp = convertDate;


                        }
                        catch
                        {
                            break;
                        }

                    }
                }
                else break;

            }

            count = 0;
            while (true)
            {
                if (count >= 100) break;
                count++;

                Match mdatetime = Regex.Match(convertDate, @"\d+\s{1}([Jj]anuary|[Ff]ebruary|[Mm]arch|[Aa]pril|[Mm]ay|[Jj]une|[Jj]uly|[Aa]ugust|[Ss]eptember|[Oo]ctober|[Nn]ovember|[Dd]ecember)\s{1}\d{4}");

                if (mdatetime.Success)
                {

                    Match mfile = Regex.Match(convertDate.Substring(mdatetime.Index), @".*\.(jpg|JPG|jpeg|JPEG|gif|ogg|OGG|GIF|flac|FLAC|svg|SVG)");
                    if (mfile.Success && mfile.Value.Contains(mdatetime.Value) == true)
                    {
                        convertDate = convertDate.Substring(mfile.Index + mfile.Value.Length);
                        convertDatetemp = convertDate;
                        continue;
                    }
                    else
                    {

                        try
                        {
                            dt = Convert.ToDateTime(mdatetime.Value);
                            a = dt.Month.ToString();
                            b = dt.Day.ToString();
                            c = dt.Year.ToString();
                            result = "ngày " + b + " tháng " + a + " năm " + c;
                            convertDate = convertDate.Replace(mdatetime.Value, result);
                            ArticleText = ArticleText.Replace(convertDatetemp, convertDate);
                            convertDatetemp = convertDate;
                        }
                        catch
                        {
                            break;
                        }

                    }

                }
                else break;

            }

            count = 0;

            while (true)
            {
                if (count >= 100) break;
                count++;

                Match mdatetime = Regex.Match(convertDate, @"([Jj]anuary|[Ff]ebruary|[Mm]arch|[Aa]pril|[Mm]ay|[Jj]une|[Jj]uly|[Aa]ugust|[Ss]eptember|[Oo]ctober|[Nn]ovember|[Dd]ecember)\s{1}\d+\s{1}\d{4}");
                if (mdatetime.Success)
                {

                    Match mfile = Regex.Match(convertDate.Substring(mdatetime.Index), @".*\.(jpg|JPG|jpeg|JPEG|gif|ogg|OGG|GIF|flac|FLAC|svg|SVG)");
                    if (mfile.Success && mfile.Value.Contains(mdatetime.Value) == true)
                    {
                        convertDate = convertDate.Substring(mfile.Index + mfile.Value.Length);
                        convertDatetemp = convertDate;
                        continue;
                    }
                    else
                    {
                        try
                        {

                            dt = Convert.ToDateTime(char.ToUpper(mdatetime.Value[0]) + mdatetime.Value.Substring(1));
                            a = dt.Month.ToString();
                            b = dt.Day.ToString();
                            c = dt.Year.ToString();
                            result = "ngày " + b + " tháng " + a + " năm " + c;
                            convertDate = convertDate.Replace(mdatetime.Value, result);
                            ArticleText = ArticleText.Replace(convertDatetemp, convertDate);
                            convertDatetemp = convertDate;

                        }
                        catch
                        {
                            break;
                        }

                    }
                }
                else break;
            }

            //Fix lỗi ngày tháng "Kiểm tra giá trị ngày tháng"
            while (true)
            {
                if (count >= 100) break;
                count++;


                Match mdatetime = Regex.Match(convertDate, @"(access-date|date)\s*=\s*\d{4}\s*-\s*\d+\s*-\s*\d+\s*(\||})");
                if (mdatetime.Success)
                {

                    Match mfile = Regex.Match(convertDate.Substring(mdatetime.Index), @".*\.(jpg|JPG|jpeg|JPEG|gif|ogg|OGG|GIF|flac|FLAC|svg|SVG)");
                    if (mfile.Success && mfile.Value.Contains(mdatetime.Value) == true)
                    {
                        convertDate = convertDate.Substring(mfile.Index + mfile.Value.Length);
                        convertDatetemp = convertDate;
                        continue;
                    }
                    else
                    {
                        try
                        {

                            //int i = mdatetime.Value.IndexOf('=');
                            //int j = mdatetime.Value.IndexOf('|');
                            string temp = mdatetime.Value.Substring(mdatetime.Value.IndexOf('=') + 1).Trim();
                            if (mdatetime.Value.Contains("|"))
                            {
                                temp = temp.Substring(0, temp.IndexOf('|')).Trim();
                            }
                            else if (mdatetime.Value.Contains("}"))
                            {
                                temp = temp.Substring(0, temp.IndexOf('}')).Trim();
                            }

                            dt = Convert.ToDateTime(temp);
                            a = dt.Month.ToString();
                            b = dt.Day.ToString();
                            c = dt.Year.ToString();

                            if (mdatetime.Value.Contains("access-date"))
                            {
                                result = "access-date = ngày " + b + " tháng " + a + " năm " + c;
                            }
                            else
                            {
                                result = "date = ngày " + b + " tháng " + a + " năm " + c;
                            }

                            if (mdatetime.Value.Contains("}"))
                            {
                                result += "}";
                            }
                            else result += " |";

                            convertDate = convertDate.Replace(mdatetime.Value, result);
                            ArticleText = ArticleText.Replace(convertDatetemp, convertDate);
                            convertDatetemp = convertDate;

                        }
                        catch (Exception ex)
                        {
                            string s = ex.Message;
                            break;
                        }

                    }
                }
                else break;
            }

            while (true)
            {
                if (count >= 100) break;
                count++;

                Match mdatetime = Regex.Match(convertDate, @"(access-date|date)\s*=\s*\d+\s*-\s*\d+\s*-\s*\d{4}\s*(\||})");
                if (mdatetime.Success)
                {

                    Match mfile = Regex.Match(convertDate.Substring(mdatetime.Index), @".*\.(jpg|JPG|jpeg|JPEG|gif|ogg|OGG|GIF|flac|FLAC|svg|SVG)");
                    if (mfile.Success && mfile.Value.Contains(mdatetime.Value) == true)
                    {
                        convertDate = convertDate.Substring(mfile.Index + mfile.Value.Length);
                        convertDatetemp = convertDate;
                        continue;
                    }
                    else
                    {
                        try
                        {
                            string temp = mdatetime.Value.Substring(mdatetime.Value.IndexOf('=') + 1).Trim();
                            if (mdatetime.Value.Contains("|"))
                            {
                                temp = temp.Substring(0, temp.IndexOf('|')).Trim();
                            }
                            else if (mdatetime.Value.Contains("}"))
                            {
                                temp = temp.Substring(0, temp.IndexOf('}')).Trim();
                            }

                            string[] s = temp.Split('-');
                            dt = Convert.ToDateTime(s[2] + "-" + s[1] + "-" + s[0]);

                            a = dt.Month.ToString();
                            b = dt.Day.ToString();
                            c = dt.Year.ToString();

                            if (mdatetime.Value.Contains("access-date"))
                            {
                                result = "access-date = ngày " + b + " tháng " + a + " năm " + c;
                            }
                            else
                            {
                                result = "date = ngày " + b + " tháng " + a + " năm " + c;
                            }

                            if (mdatetime.Value.Contains("}"))
                            {
                                result += "}";
                            }
                            else result += " |";

                            convertDate = convertDate.Replace(mdatetime.Value, result);
                            ArticleText = ArticleText.Replace(convertDatetemp, convertDate);
                            convertDatetemp = convertDate;

                        }
                        catch
                        {
                            break;
                        }

                    }
                }
                else break;
            }

            #region Fix lỗi 2ngày 2 tháng 4 năm 2012
            while (true)
            {
                if (count >= 100) break;
                count++;

                Match mdatetime = Regex.Match(convertDate, @"\d+[Nn]gày\s{1}\d+\s{1}tháng");
                if (mdatetime.Success)
                {

                    Match mfile = Regex.Match(convertDate.Substring(mdatetime.Index), @".*\.(jpg|JPG|jpeg|JPEG|gif|ogg|OGG|GIF|flac|FLAC|svg|SVG)");
                    if (mfile.Success && mfile.Value.Contains(mdatetime.Value) == true)
                    {
                        convertDate = convertDate.Substring(mfile.Index + mfile.Value.Length);
                        convertDatetemp = convertDate;
                        continue;
                    }
                    else
                    {
                        try
                        {

                            //dt = Convert.ToDateTime(char.ToUpper(mdatetime.Value[0]) + mdatetime.Value.Substring(1));

                            b = mdatetime.Value.Substring(0, 1) + mdatetime.Value.Substring(mdatetime.Value.IndexOf("ngày ") + 5, 1);

                            result = "ngày " + b + " tháng";
                            convertDate = convertDate.Replace(mdatetime.Value, result);

                            ArticleText = ArticleText.Replace(convertDatetemp, convertDate);
                            convertDatetemp = convertDate;



                        }
                        catch
                        {
                            break;
                        }

                    }
                }
                else break;
            }
            #endregion
            return ArticleText;

        }

        /// <summary>
        /// Dịch tiếng Anh sang tiếng Việt các cụm từ phổ biến
        /// </summary>
        /// <param name="ArticleText"></param>
        /// <returns></returns>
        public string TranslateCommon(string ArticleText)
        {
            ArticleText = Regex.Replace(ArticleText, @"\{\{\s*[Tt]ham\s*_\s*[Kk]hảo", "{{tham khảo");
            ArticleText = Regex.Replace(ArticleText, @"\[\[[Cc]ategory\s*:", "[[Thể loại:");
            ArticleText = Regex.Replace(ArticleText, @"\{\{[Cc]ite book", "{{chú thích sách");
            ArticleText = Regex.Replace(ArticleText, @"\{\{[Cc]ite web", "{{chú thích web");
            ArticleText = Regex.Replace(ArticleText, @"\{\{[Cc]ite news", "{{chú thích báo");
            ArticleText = Regex.Replace(ArticleText, @"\{\{[Cc]ite journal", "{{chú thích tạp chí");
            ArticleText = Regex.Replace(ArticleText, @"\{\{[Cc]ite iucn", "{{chú thích IUCN");
            ArticleText = Regex.Replace(ArticleText, @"\{\{[Cc]ite doi", "{{chú thích DOI");
            ArticleText = Regex.Replace(ArticleText, @"\{\{[Cc]ite tweet", "{{chú thích tweet");
            ArticleText = Regex.Replace(ArticleText, @"\{\{[Rr]eflist", "{{tham khảo");
            ArticleText = Regex.Replace(ArticleText, @"\<[Rr]eferences\s*\/\>", "{{tham khảo}}");
            ArticleText = Regex.Replace(ArticleText, @"\[\[[Ff]ile\s*:", "[[Tập tin:");
            ArticleText = Regex.Replace(ArticleText, @"\[\[[Ii]mage\s*:", "[[Hình:");
            ArticleText = Regex.Replace(ArticleText, @"\{\{[Tt]axobox", "{{Bảng phân loại");
            ArticleText = Regex.Replace(ArticleText, @"\{\{[Cc]ommonscat-inline", "{{Thể loại Commons nội dòng");
            ArticleText = Regex.Replace(ArticleText, @"\{\{[Cc]ommons category-inline", "{{Thể loại Commons nội dòng");
            ArticleText = Regex.Replace(ArticleText, @"\{\{[Ww]ikispecies-inline", "{{Wikispecies nội dòng");
            ArticleText = Regex.Replace(ArticleText, @"\{\{[Cc]ommons category", "{{Thể loại Commons");
            ArticleText = Regex.Replace(ArticleText, @"\{\{[Cc]ommons\s*cat", "{{Thể loại Commons");
            //ArticleText = ArticleText.Replace("\n ", "\n");

            ArticleText = Regex.Replace(ArticleText, @"==\s*[Ee]xternal\s*links\s*==", "== Liên kết ngoài ==");
            ArticleText = Regex.Replace(ArticleText, @"==\s*[Rr]eferences\s*==", "== Tham khảo ==");
            ArticleText = Regex.Replace(ArticleText, @"==\s*[Ss]ee\s*also\s*==", "== Xem thêm ==");
            ArticleText = Regex.Replace(ArticleText, @"==\s*[Ff]urther\s*reading\s*==", "== Đọc thêm ==");
            ArticleText = Regex.Replace(ArticleText, @"==\s*Notes\s*==", "== Ghi chú ==");
            ArticleText = Regex.Replace(ArticleText, @"accessdate\s*=", "access-date =");

            // lặp 2 lần Thể loại: do công cụ Content Translation gây ra
            ArticleText = Regex.Replace(ArticleText, @"\[\[\s*Thể\s*loại\s*:\s*Category\s*:", "[[Thể loại:");
            ArticleText = Regex.Replace(ArticleText, @"\[\[\s*Thể\s*loại\s*:\s*Thể\s*loại\s*:", "[[Thể loại:");

            ArticleText = ArticleText.Replace(". Retrieved on", ". Truy cập");
            ArticleText = ArticleText.Replace(". Retrieved", ". Truy cập");
            ArticleText = ArticleText.Replace(". Accessed", ". Truy cập");
            ArticleText = ArticleText.Replace(":Living people]]", ":Nhân vật còn sống]]");

            ArticleText = Regex.Replace(ArticleText, @"\|\s*trans_title\s*=", "|trans-title=");
            ArticleText = Regex.Replace(ArticleText, @"\|\s*trans_chapter\s*=", "|trans-chapter=");
            ArticleText = Regex.Replace(ArticleText, @"\|\s*dead-url\s*=\s*yes", "|url-status=dead");
            ArticleText = Regex.Replace(ArticleText, @"\|\s*dead-url\s*=\s*no", "|url-status=live");
            ArticleText = Regex.Replace(ArticleText, @"\|\s*dead-url\s*=", "|url-status=");
            ArticleText = Regex.Replace(ArticleText, @"\|\s*subscription\s*=\s*yes", "|url-access=subscription");
            ArticleText = Regex.Replace(ArticleText, @"\|\s*registration\s*=\s*yes", "|url-access=registration");

            // Bỏ tham số coauthor trống (lỗi gây ra ở bản mẫu CS1)
            ArticleText = Regex.Replace(ArticleText, @"\|\s*coauthor\s*=\s*\|", "|");
            ArticleText = Regex.Replace(ArticleText, @"\|\s*coauthors\s*=\s*\|", "|");

       

            // Bỏ tham số |df= thì cần thời gian test

            //ArticleText = ArticleText.Replace("&nbsp;", " ");

            ////Tạm thời
            //if (ArticleText.Contains("{{Taxobox") || ArticleText.Contains("{{taxobox"))
            //{
            //    ArticleText = ArticleText.Replace("{{tham khảo}}", "");
            //    ArticleText = ArticleText.Replace("{{tham khảo|2}}", "");
            //    ArticleText = ArticleText.Replace("{{Tham khảo}}", "");
            //    ArticleText = ArticleText.Replace("{{Tham khảo|2}}", "");
            //}


            return ArticleText;
        }

        /// <summary>
        /// Sửa lỗi khoảng trắng trước, sau dấu câu
        /// </summary>
        /// <param name="ArticleText"></param>
        /// <param name="ArticleTitle"></param>
        /// <returns></returns>
        public string PunctuationFixes(string ArticleText, string ArticleTitle)
        {
            #region Punctuation

            string convertPunctuation = ArticleText;
            string convertPunctuationTemp = ArticleText;

            //Exclude internet domain articles
            Match domainname = Regex.Match(ArticleTitle, @"\.\w{2}");

            if (!ArticleText.Contains("Tên miền") && !domainname.Success)
            {


                int count = 0;
                // ArticleText = ArticleText + "_________";
                while (true)
                {
                    if (count >= 100) break;
                    count++;

                    Match punctuation = Regex.Match(convertPunctuation, @"\w{1}\s{1,2}[.,;:)]");
                    //[\p{P}-[{}(*-]]

                    if (punctuation.Success)
                    {
                        // Tạm bỏ ;: vì lỗi đầu dòng
                        Match error = Regex.Match(punctuation.Value, @"\w{1}\s{1,2}\n[.,;:)]");

                        if (error.Success)
                        {
                            convertPunctuation = convertPunctuation.Substring(error.Index + error.Value.Length);
                            convertPunctuationTemp = convertPunctuation;
                            continue;
                        }

                        Match mfile = Regex.Match(convertPunctuation.Substring(punctuation.Index), @".*\.(jpg|JPG|jpeg|JPEG|gif|ogg|OGG|GIF|flac|FLAC|svg|SVG)");
                        if (mfile.Success && mfile.Value.Contains(punctuation.Value) == true)
                        {
                            convertPunctuation = convertPunctuation.Substring(mfile.Index + mfile.Value.Length);
                            convertPunctuationTemp = convertPunctuation;
                            continue;
                        }
                        else
                        {
                            try
                            {

                                convertPunctuation = convertPunctuation.Replace(punctuation.Value, punctuation.Value.Substring(0, punctuation.Value.Length - 2) + punctuation.Value.Substring(punctuation.Value.Length - 1, 1));
                                ArticleText = ArticleText.Replace(convertPunctuationTemp, convertPunctuation);
                                convertPunctuationTemp = convertPunctuation;

                                //ArticleText = "_______: " + punctuation.Value;



                            }
                            catch
                            {

                                break;
                            }


                        }

                    }
                    else break;

                }
                convertPunctuation = ArticleText;
                convertPunctuationTemp = ArticleText;
                count = 0;
                while (true)
                {
                    if (count >= 100) break;
                    count++;

                    Match punctuation = Regex.Match(convertPunctuation, @"[(]\s{1,2}\w{1}");
                    //[\p{P}-[{}).,:;_*]]
                    if (punctuation.Success)
                    {

                        Match mfile = Regex.Match(convertPunctuation.Substring(punctuation.Index), @".*\.(jpg|JPG|jpeg|JPEG|gif|ogg|OGG|GIF|flac|FLAC|svg|SVG|svg|SVG)");
                        if (mfile.Success && mfile.Value.Contains(punctuation.Value) == true)
                        {
                            convertPunctuation = convertPunctuation.Substring(mfile.Index + mfile.Value.Length);
                            convertPunctuationTemp = convertPunctuation;
                            continue;
                        }
                        else
                        {
                            try
                            {

                                convertPunctuation = convertPunctuation.Replace(punctuation.Value, punctuation.Value.Substring(0, 1) + punctuation.Value.Substring(2));
                                ArticleText = ArticleText.Replace(convertPunctuationTemp, convertPunctuation);
                                convertPunctuationTemp = convertPunctuation;

                                //ArticleText = "_______: " + punctuation.Value;



                            }
                            catch
                            {

                                break;
                            }


                        }

                    }
                    else break;

                }

                count = 0;

                //Trường hợp ( [[abc]]) => ([[abc]])
                while (true)
                {
                    if (count >= 100) break;
                    count++;

                    Match punctuation = Regex.Match(convertPunctuation, @"[(]\s{1,2}\[\[\w{1}");
                    //[\p{P}-[{}).,:;_*]]
                    if (punctuation.Success)
                    {

                        Match mfile = Regex.Match(convertPunctuation.Substring(punctuation.Index), @".*\.(jpg|JPG|jpeg|JPEG|gif|ogg|OGG|GIF|flac|FLAC|svg|SVG|svg|SVG)");
                        if (mfile.Success && mfile.Value.Contains(punctuation.Value) == true)
                        {
                            convertPunctuation = convertPunctuation.Substring(mfile.Index + mfile.Value.Length);
                            convertPunctuationTemp = convertPunctuation;
                            continue;
                        }
                        else
                        {
                            try
                            {

                                convertPunctuation = convertPunctuation.Replace(punctuation.Value, punctuation.Value.Substring(0, 1) + punctuation.Value.Substring(2));
                                ArticleText = ArticleText.Replace(convertPunctuationTemp, convertPunctuation);
                                convertPunctuationTemp = convertPunctuation;

                                //ArticleText = "_______: " + punctuation.Value;



                            }
                            catch
                            {

                                break;
                            }


                        }

                    }
                    else break;

                }

                count = 0;

                while (true)
                {

                    if (count >= 100) break;
                    count++;

                    Match punctuation = Regex.Match(convertPunctuation, @"\w{1}\]\]\s{1,2}[.,;:)]");
                    //[\p{P}-[{}).,:;_*]]
                    if (punctuation.Success)
                    {
                        // Sửa ;: vì lỗi đầu dòng
                        Match error = Regex.Match(punctuation.Value, @"\w{1}\]\]\s{1,2}\n[.,;:)]");

                        if (error.Success)
                        {
                            convertPunctuation = convertPunctuation.Substring(error.Index + error.Value.Length);
                            convertPunctuationTemp = convertPunctuation;
                            continue;
                        }

                        Match mfile = Regex.Match(convertPunctuation.Substring(punctuation.Index), @".*\.(jpg|JPG|jpeg|JPEG|gif|ogg|OGG|GIF|flac|FLAC|svg|SVG)");
                        if (mfile.Success && mfile.Value.Contains(punctuation.Value) == true)
                        {
                            convertPunctuation = convertPunctuation.Substring(mfile.Index + mfile.Value.Length);
                            convertPunctuationTemp = convertPunctuation;
                            continue;
                        }
                        else
                        {
                            try
                            {

                                convertPunctuation = convertPunctuation.Replace(punctuation.Value, punctuation.Value.Substring(0, 3) + punctuation.Value.Substring(4));
                                ArticleText = ArticleText.Replace(convertPunctuationTemp, convertPunctuation);
                                convertPunctuationTemp = convertPunctuation;





                            }
                            catch
                            {

                                break;
                            }


                        }

                    }
                    else break;

                }

            }

            #endregion
            return ArticleText;
        }


        //public string SetStub(string ArticleText)
        //{

        //    if (ASCIIEncoding.Unicode.GetByteCount(ArticleText) <= 3000)
        //    {
        //        ArticleText += "\r\n" + "{{sơ khai}}";
        //    }

        //    return ArticleText;

        //}

        /// <summary>
        /// Kiểm tra và đặt mục ==Tham khảo== và thẻ {{tham khảo}} vào bài
        /// </summary>
        /// <param name="ArticleText"></param>
        /// <returns></returns>
        public string SetReference(string ArticleText, int wikiNamespace)
        {
            if (wikiNamespace != 0) return ArticleText;

            //Các bản mẫu định hướng, redirect
            Match dis = Regex.Match(ArticleText, @"\{\{\s*[Dd][Ii][Ss]");
            Match dab = Regex.Match(ArticleText, @"\{\{\s*[Dd][Aa][Bb]");
            Match dinhhuong = Regex.Match(ArticleText, @"\{\{\s*[Đđ][Ịị][Nn][Hh]\s*[Hh][Ưư][Ớớ][Nn][Gg]");
            Match trangdinhhuong = Regex.Match(ArticleText, @"\{\{[Tt]rang\s*[Đđ]ịnh\s*[Hh]ướng");
            Match TLAdisambig = Regex.Match(ArticleText, @"\{\{\s*[Tt][Ll][Aa]disambig");
            Match redirectvn = Regex.Match(ArticleText, @"\#\s*[Đđ][Ổổ][Ii]");
            Match redirect = Regex.Match(ArticleText, @"\#\s*[Rr][Ee][Dd][Ii][Rr][Ee][Cc][Tt]");


            if (dis.Success || dab.Success || dinhhuong.Success || TLAdisambig.Success || redirectvn.Success || redirect.Success || trangdinhhuong.Success) return ArticleText;

            //Bản mẫu chú thích
            Match reflist = Regex.Match(ArticleText, @"\{\{\s*[Rr][eé]f");
            Match thamkhao = Regex.Match(ArticleText, @"\{\{[Tt]ham\s*[Kk]hảo");
            Match references = Regex.Match(ArticleText, @"\<\s*[Rr]eferences");
            Match notes = Regex.Match(ArticleText, @"\{\{[Nn]ote");

            //Nguồn
            Match sfn = Regex.Match(ArticleText, @"\{\{\s*[Ss]fn");
            Match refTag = Regex.Match(ArticleText, @"\{\{\s*[Rr]efTag");
            Match refs = Regex.Match(ArticleText, @"\<\s*[Rr]ef");

            Match thamkhaosection = Regex.Match(ArticleText, @"==\s*[Tt]ham\s*[Kk]hảo\s*==");
            Match chuthichsection = Regex.Match(ArticleText, @"==\s*[Cc]hú\s*[Tt]hích\s*==");
            Match category = Regex.Match(ArticleText, @"\[\[[Tt]hể\s*[Ll]oại");
            Match externalLink = Regex.Match(ArticleText, @"==\s*[Ll]iên\s*[Kk]ết\s*[Nn]goài\s*==");
            Match stub = Regex.Match(ArticleText, @"\{\{[Ss]ơ\s*[Kk]hai");
            Match stubEnglish = Regex.Match(ArticleText, @"\{\{.*stub.*\}\}");
            Match verystub = Regex.Match(ArticleText, @"\{\{[Rr]ất\s*[Ss]ơ\s*[Kk]hai");
            Match taxobox = Regex.Match(ArticleText, @"\{\{[Tt]axobox");

            // Add nhãn sơ khai
            if (ASCIIEncoding.Unicode.GetByteCount(ArticleText) <= 5000 && !stub.Success && !verystub.Success && !stubEnglish.Success)
            {
                if (category.Success)
                {
                    if (taxobox.Success) return ArticleText.Insert(category.Index, "{{sơ khai sinh học}}\r\n");
                    else return ArticleText.Insert(category.Index, "{{sơ khai}}\r\n");
                }
                else
                {
                    if (taxobox.Success) ArticleText += "\r\n" + "{{sơ khai sinh học}}";
                    else ArticleText += "\r\n" + "{{sơ khai}}";

                }
                //Set lại vị trí nếu đã thêm bản mẫu Sơ khai
                stub = Regex.Match(ArticleText, @"\{\{[Ss]ơ\s*[Kk]hai");
            }

            // Add nhãn tham khảo
            if (!reflist.Success && !thamkhao.Success && !references.Success && !notes.Success)
            {
                if (thamkhaosection.Success) return ArticleText.Insert(thamkhaosection.Index + thamkhaosection.Value.Length, "\r\n{{tham khảo}}");
                if (chuthichsection.Success) return ArticleText.Insert(chuthichsection.Index + chuthichsection.Value.Length, "\r\n{{tham khảo}}");
                if (externalLink.Success) return ArticleText.Insert(externalLink.Index, "==Tham khảo==\r\n{{tham khảo}}\r\n");
                if (stub.Success) return ArticleText.Insert(stub.Index, "==Tham khảo==\r\n{{tham khảo}}\r\n");
                if (verystub.Success) return ArticleText.Insert(verystub.Index, "==Tham khảo==\r\n{{tham khảo}}\r\n");
                if (category.Success) return ArticleText.Insert(category.Index, "==Tham khảo==\r\n{{tham khảo}}\r\n");

                return ArticleText + "\r\n" + "==Tham khảo==\r\n{{tham khảo}}\r\n";
            }

            // Kiểm tra trang định hướng với tiêu đề bài viết

            return ArticleText;

        }