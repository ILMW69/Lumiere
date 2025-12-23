# Sample Questions for Demo

**Purpose:** Pre-tested questions that reliably demonstrate Lumiere's capabilities  
**Status:** ✅ Verified on deployment  
**Last Updated:** December 23, 2025

---

## 📋 Document Preparation

### Recommended Documents to Upload:

1. **AI/ML Technical Document** (Primary)
   - Example: "Introduction to Machine Learning" PDF
   - Why: Contains clear concepts for RAG demonstration
   - Size: 5-20 pages ideal
   - Download: Use any ML tutorial or textbook chapter

2. **Business Report** (Secondary)
   - Example: Company annual report, market analysis
   - Why: Shows enterprise use case
   - Size: 10-30 pages
   - Optional for time

3. **Research Paper** (Tertiary)
   - Example: Academic paper on NLP/LLMs
   - Why: Demonstrates technical content handling
   - Size: 8-12 pages
   - Optional for time

### Quick Test Documents:
If you need a quick document, create a simple text file:

```text
Title: Machine Learning Basics

Machine learning has three main types:

1. Supervised Learning
Supervised learning uses labeled training data. The algorithm learns 
from examples where the correct answer is known. Common algorithms 
include linear regression, decision trees, and neural networks.

2. Unsupervised Learning  
Unsupervised learning works with unlabeled data. The algorithm finds 
patterns without being told what to look for. Examples include 
clustering algorithms like K-means and dimensionality reduction 
techniques like PCA.

3. Reinforcement Learning
Reinforcement learning learns through trial and error. An agent takes 
actions in an environment and receives rewards or penalties. This is 
used in robotics, game playing, and autonomous systems.

Deep learning is a subset of machine learning that uses neural networks 
with multiple layers. It has revolutionized computer vision, natural 
language processing, and speech recognition.
```

Save as: `ml_basics.txt` or convert to PDF

---

## 🎯 Mode 1: All-In Mode Questions

### Question Set A: RAG-Only Query

**Question 1 (Simple):**
```
What are the main types of machine learning mentioned in the document?
```

**Expected Behavior:**
- ✅ Routes to: Intent → Retrieval → Reasoning → Critic → Memory
- ✅ Shows: Answer with bullet points (supervised, unsupervised, reinforcement)
- ✅ Sources: Document chunks cited at bottom
- ✅ Time: ~5-8 seconds

**Question 2 (Definition):**
```
Explain supervised learning based on the document
```

**Expected Behavior:**
- ✅ Routes to: Same path as Q1
- ✅ Shows: Definition with examples from document
- ✅ Sources: Specific chunk containing supervised learning section
- ✅ Time: ~5-8 seconds

---

### Question Set B: SQL-Only Query

**Question 1 (Simple Select):**
```
Show me all customers
```

**Expected Behavior:**
- ✅ Routes to: Intent → SQL Execution → SQL Reasoning → Critic → Memory
- ✅ Shows: Table with customer data
- ✅ SQL Query: `SELECT * FROM customers LIMIT 10;`
- ✅ Time: ~3-5 seconds

**Question 2 (Aggregation):**
```
What is the total sales amount?
```

**Expected Behavior:**
- ✅ Routes to: Same SQL path
- ✅ Shows: Single number (sum of sales)
- ✅ SQL Query: `SELECT SUM(amount) FROM sales;`
- ✅ Time: ~3-5 seconds

**Question 3 (Top N):**
```
Show me the top 5 customers by total sales
```

**Expected Behavior:**
- ✅ Routes to: Same SQL path
- ✅ Shows: Table with 5 rows (customer name, total)
- ✅ SQL Query: JOIN with GROUP BY and ORDER BY
- ✅ Time: ~4-6 seconds

---

### Question Set C: Visualization Queries

**Question 1 (Bar Chart):**
```
Create a bar chart showing total sales by car model
```

**Expected Behavior:**
- ✅ Routes to: Intent → SQL Execution → SQL Reasoning → Visualization → Critic → Memory
- ✅ Shows: Interactive Plotly bar chart
- ✅ SQL Query: JOIN with GROUP BY
- ✅ Chart: X-axis=car models, Y-axis=sales amount
- ✅ Time: ~6-10 seconds

**Question 2 (Comparison):**
```
Visualize sales comparison between different car brands
```

**Expected Behavior:**
- ✅ Routes to: Same path
- ✅ Shows: Bar or pie chart
- ✅ Interactive: Hover shows exact values
- ✅ Time: ~6-10 seconds

**Question 3 (Time Series - if date data available):**
```
Show me the sales trend over time
```

**Expected Behavior:**
- ✅ Routes to: Same path
- ✅ Shows: Line chart
- ✅ X-axis: Time, Y-axis: Sales
- ✅ Time: ~6-10 seconds

---

### Question Set D: Hybrid Queries (⭐ SHOWCASE)

**Question 1 (RAG + SQL):**
```
Based on the document, explain supervised learning and then show me the sales data for customers who made purchases over $1000
```

**Expected Behavior:**
- ✅ Routes to: Intent → Retrieval → Reasoning → SQL Execution → SQL Reasoning → Critic → Memory
- ✅ Shows: 
  1. Explanation of supervised learning from document
  2. Table of customers with sales > $1000
- ✅ Demonstrates: Multi-step reasoning
- ✅ Time: ~10-15 seconds

**Question 2 (General + SQL):**
```
What is the difference between classification and regression, and show me which customers bought SUVs
```

**Expected Behavior:**
- ✅ Routes to: Intent → General Reasoning → SQL path
- ✅ Shows: 
  1. Explanation of classification vs regression
  2. Table of customers who bought SUVs
- ✅ Time: ~10-15 seconds

---

### Question Set E: General Knowledge Queries

**Question 1 (No RAG Needed):**
```
What is Python?
```

**Expected Behavior:**
- ✅ Routes to: Intent → General Reasoning → Critic → Memory
- ✅ Shows: General explanation of Python (not from documents)
- ✅ Note: Shows system can handle queries outside uploaded docs
- ✅ Time: ~4-6 seconds

**Question 2 (Current Events):**
```
Explain what GPT-4 is
```

**Expected Behavior:**
- ✅ Routes to: Same general path
- ✅ Shows: General knowledge answer
- ✅ Time: ~4-6 seconds

---

## 🎯 Mode 2: Chat with RAG Questions

### Question Set F: Document Q&A

**Question 1 (Direct):**
```
What types of machine learning are discussed?
```

**Expected Behavior:**
- ✅ Routes to: Intent → Retrieval → Reasoning → Critic → Memory
- ✅ Shows: Answer from document only
- ✅ Time: ~5-8 seconds

**Question 2 (Follow-up - CONTEXT DEMO):**
```
Can you explain that in simpler terms?
```

**Expected Behavior:**
- ✅ Uses conversation history to understand "that" = previous topic
- ✅ Shows: Simplified explanation of same content
- ✅ Demonstrates: Context awareness
- ✅ Time: ~5-8 seconds

**Question 3 (Anaphora Resolution):**
```
Give me an example of it
```

**Expected Behavior:**
- ✅ Resolves "it" from conversation history
- ✅ Shows: Example from document
- ✅ Time: ~5-8 seconds

---

### Question Set G: Source Verification

**Question 1 (Specific):**
```
What page discusses neural networks?
```

**Expected Behavior:**
- ✅ Shows: Answer with specific source citation
- ✅ Sources: [doc_id:chunk_index] clearly visible
- ✅ Demonstrates: Traceability
- ✅ Time: ~5-8 seconds

**Question 2 (Multi-source):**
```
Compare the definitions of supervised and unsupervised learning
```

**Expected Behavior:**
- ✅ Shows: Comparison from document
- ✅ Sources: Multiple chunks cited
- ✅ Time: ~6-10 seconds

---

## 🎯 Mode 3: Data Analyst Questions

### Question Set H: Basic SQL

**Question 1 (Simple):**
```
How many customers do we have?
```

**Expected Behavior:**
- ✅ SQL: `SELECT COUNT(*) FROM customers;`
- ✅ Shows: Single number
- ✅ Time: ~3-5 seconds

**Question 2 (Filter):**
```
Show me customers from New York
```

**Expected Behavior:**
- ✅ SQL: `SELECT * FROM customers WHERE city = 'New York';`
- ✅ Shows: Filtered table
- ✅ Time: ~3-5 seconds

---

### Question Set I: Complex SQL

**Question 1 (JOIN):**
```
Which customers bought the most expensive cars?
```

**Expected Behavior:**
- ✅ SQL: JOIN customers, sales, cars with ORDER BY price
- ✅ Shows: Table with customer names and car details
- ✅ Time: ~5-8 seconds

**Question 2 (Aggregation + GROUP BY):**
```
What is the average sale amount per customer?
```

**Expected Behavior:**
- ✅ SQL: GROUP BY with AVG()
- ✅ Shows: Customer name and average
- ✅ Time: ~5-8 seconds

---

### Question Set J: Visualizations

**Question 1 (Distribution):**
```
Create a histogram of car prices
```

**Expected Behavior:**
- ✅ Shows: Histogram (Plotly)
- ✅ Interactive: Hover shows bin counts
- ✅ Time: ~6-10 seconds

**Question 2 (Comparison):**
```
Show a pie chart of sales by car type
```

**Expected Behavior:**
- ✅ Shows: Pie chart
- ✅ Interactive: Click to highlight segments
- ✅ Time: ~6-10 seconds

**Question 3 (Multi-series):**
```
Compare sales performance across different car brands
```

**Expected Behavior:**
- ✅ Shows: Grouped bar chart or stacked chart
- ✅ Time: ~6-10 seconds

---

## 🔄 Context & Memory Demonstration

### Question Sequence K: Memory Test

**Step 1:**
```
What is supervised learning?
```
→ Get answer from document

**Step 2:**
```
Can you simplify that?
```
→ System remembers "that" = supervised learning

**Step 3:**
```
Give me a real-world example
```
→ System continues the conversation thread

**Step 4:**
```
How does this differ from unsupervised learning?
```
→ System uses "this" from context

**Expected Behavior:**
- ✅ All 4 questions answered correctly without re-specifying topic
- ✅ Demonstrates: Natural conversation flow
- ✅ Shows: Session memory working

---

## 🚨 Edge Cases & Error Handling

### Question Set L: Error Scenarios

**Question 1 (No Documents):**
```
Tell me about quantum computing from my documents
```

**Expected Behavior (if no relevant docs uploaded):**
- ✅ System: "I don't have documents about quantum computing"
- ✅ Fallback: May route to general reasoning
- ✅ Shows: Graceful error handling

**Question 2 (Ambiguous SQL):**
```
Show me the data
```

**Expected Behavior:**
- ✅ System: Asks for clarification OR shows all tables
- ✅ Shows: Handles vague queries

**Question 3 (Invalid SQL Request):**
```
Delete all customers
```

**Expected Behavior:**
- ✅ System: Only SELECT queries allowed (read-only)
- ✅ Shows: Security measures

---

## ✅ Pre-Demo Testing Checklist

Test these the morning of your defense:

- [ ] Upload document successfully
- [ ] Test Q1 from Set A (simple RAG)
- [ ] Test Q1 from Set C (visualization)
- [ ] Test Q1 from Set D (hybrid query)
- [ ] Test follow-up question (Set F Q2)
- [ ] Check LangSmith traces are logging
- [ ] Verify source citations appear
- [ ] Confirm charts are interactive

---

## 📊 Question Selection Strategy

### For 12-Minute Demo:

**Must Include (Core Features):**
1. ✅ Document upload (Set A)
2. ✅ Simple RAG query (Set A Q1)
3. ✅ Hybrid query (Set D Q1) ⭐ SHOWCASE
4. ✅ Follow-up with context (Set F Q2) ⭐ MEMORY DEMO
5. ✅ SQL query (Set B Q3)
6. ✅ Visualization (Set C Q1) ⭐ VISUAL IMPACT

**Optional (Time Permitting):**
7. General knowledge query (Set E)
8. Error handling (Set L)
9. Complex SQL (Set I)

**Skip If Short on Time:**
- Multiple visualizations
- All three modes (focus on All-In)
- Edge cases

---

## 💡 Tips for Question Selection

1. **Pre-test Everything**
   - Run each question you plan to use 2-3 times
   - Note the exact response time
   - Verify outputs are good quality

2. **Have Backups**
   - Prepare 2-3 backup questions per category
   - If one fails, switch to backup immediately

3. **Know Your Answers**
   - Memorize what the system SHOULD return
   - Spot errors immediately during demo

4. **Time Management**
   - Practice with a timer
   - Know which questions to skip if running late

---

## 🎯 Golden Rule

**"If it doesn't work in practice, don't use it in the demo!"**

Only include questions you've successfully tested multiple times. Murphy's Law applies to live demos.

---

**Ready to impress! 🚀**
